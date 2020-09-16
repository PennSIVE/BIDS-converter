import argparse
import pathlib
import shutil
import glob
import csv
import re
import os

"""
takes modality string extracted from (presumably dcm2niix) converted files
returns standardized BIDS modality string
"""
def standardize_modality(modality, input_labels, output_labels=["T1w", "T2w", "FLAIR", "PD"], default_guesses=["T1", "T2", "FLAIR", "PD"]):
    if len(input_labels) != len(output_labels) != len(default_guesses):
        raise ValueError("The indices of input_labels, output_labels, default_guesses should correspond")
    modality_upper = modality.upper()
    for i in range(len(output_labels)):
        if len(input_labels[i]) == 0:
            # then just guess that if e.g. it has T1 in the name it's a T1
            if default_guesses[i] in modality_upper:
                return output_labels[i]
        else:
            # check all the possible labels
            for label in input_labels[i]:
                if label in modality_upper.replace("_", ""):
                    return output_labels[i]
    return None


def create(args):
    regex = r"\{(.*?)\}"
    placeholders = re.findall(regex, args.p)
    easier_to_parse = "{}" + args.p + "{}"
    if not args.s:
        if 'subject' in placeholders:
            before_subj = re.findall(
                r"(.*)\}(.*)\{subject\}", easier_to_parse)[0][1]  # get 2nd match group
            after_subj = re.findall(r"\{subject\}(.*?)\{", easier_to_parse)[0]
        else:
            raise ValueError(
                "Must specify subject key in -p path or via -s option")
    if not args.ss:
        if 'session' in placeholders:
            before_session = re.findall(
                r"(.*)\}(.*)\{session\}", easier_to_parse)[0][1]
            after_session = re.findall(
                r"\{session\}(.*?)\{", easier_to_parse)[0]
        else:
            raise ValueError(
                "Must specify session key in -p path or via -ss option")
    if not args.m:
        if 'modality' in placeholders:
            before_modality = re.findall(
                r"(.*)\}(.*)\{modality\}", easier_to_parse)[0][1]
            after_modality = re.findall(
                r"\{modality\}(.*?)\{", easier_to_parse)[0]
        else:
            raise ValueError(
                "Must specify modality key in -p path or via -m option")

    subjects = []  # needed for particpants.tsv
    path = re.sub(regex, '*', args.p)
    for p in glob.glob(path):
        if not p.endswith(".nii.gz"):
            print(p, "does not end with .nii.gz; skipping")
            continue
        if args.s:
            subj = args.s
        else:
            subj = p[p.find(before_subj) + len(before_subj):p.find(after_subj)]
        subjects.append(subj)
        if args.ss:
            session = args.ss
        else:
            ses_index = p.find(before_session) + len(before_session)
            session = p[ses_index: ses_index +
                        p[ses_index:].find(after_session)]
        if args.m:
            modality = args.m
        else:
            messy_modality = p[p.find(before_modality) +
                               len(before_modality):p.find(after_modality)]
            modality = standardize_modality(messy_modality, [
                                            args.t1_labels, args.t2_labels, args.flair_labels, args.pd_labels])
            if modality == None:
                print("Unrecognized modality '%s'" % (messy_modality))
                continue
        pathlib.Path(args.o + "/sub-"+subj+"/ses-"+session +
                     "/anat").mkdir(parents=True, exist_ok=True)
        run = 1
        destination = args.o + "/sub-"+subj+"/ses-"+session+"/anat/sub-" + \
            subj+"_ses-"+session+"_run-" + \
            str(run).zfill(3)+"_"+modality+".nii.gz"
        already_run = False
        while os.path.isfile(destination):
            # check if resolved symlink is same as path we're trying to copy
            if os.path.realpath(destination) == p:
                # we want to be idempotent if encountering already copied files
                already_run = True
                break
            run += 1
            destination = args.o + "/sub-"+subj+"/ses-"+session+"/anat/sub-" + \
                subj+"_ses-"+session+"_run-" + \
                str(run).zfill(3)+"_"+modality+".nii.gz"
        if already_run:
            continue

        if args.symlink:
            os.symlink(p, destination)
        else:
            shutil.copyfile(p, destination)
        with open(args.o + "/sub-"+subj+"/ses-"+session+"/anat/sub-"+subj+"_ses-"+session+"_run-001_"+modality+".json", 'w') as f:
            f.write("{}")
        with open(args.o + "/sub-"+subj+"/ses-"+session+"/anat/sub-"+subj+"_ses-"+session+"_scans.json", 'w') as f:
            f.write("{}")
        with open(args.o + "/sub-"+subj+"/ses-"+session+"/sub-"+subj+"_ses-"+session+"_scans.tsv", 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            if not f.readable():
                writer.writerow(['filename', 'acq_time'])
            writer.writerow(
                ['anat/' + os.path.basename(p), '1970-01-01T00:00:00'])

    # other req'd BIDS meta data
    with open(args.o + '/dataset_description.json', 'w') as f:
        f.write('{"Acknowledgements":"TODO: whom you want to acknowledge","Authors":["TODO:","First1 Last1","First2 Last2","..."],"BIDSVersion":"1.0.1","DatasetDOI":"TODO: eventually a DOI for the dataset","Funding":["TODO","GRANT #1","GRANT #2"],"HowToAcknowledge":"TODO: describe how to acknowledge -- either cite a corresponding paper, or just in acknowledgement section","License":"TODO: choose a license, e.g. PDDL (http://opendatacommons.org/licenses/pddl/)","Name":"TODO: name of the dataset","ReferencesAndLinks":["TODO","List of papers or websites"]}')
    with open(args.o + '/participants.json', 'w') as f:
        f.write("{}")
    with open(args.o + '/README', 'w') as f:
        f.write("TODO")
    with open(args.o + '/participants.tsv', 'w') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['participant_id', 'age', 'sex'])
        for s in subjects:
            writer.writerow(['sub-' + s, 'N/A', '0000'])


def main():
    parser = argparse.ArgumentParser(
        description='Pattern-match Nifti directories to create BIDS dataset')
    parser.add_argument('-p', type=str, action='store',
                        help='Path to Niftis with placeholders specifying subject, session, modality')
    parser.add_argument('-s', type=str, action='store', help='Subject')
    parser.add_argument('-ss', type=str, action='store', help='Session')
    parser.add_argument('-m', type=str, action='store', help='Modality')
    parser.add_argument('-o', type=str, default="/output",
                        action='store', help='Output directory')
    parser.add_argument('--symlink', default=False, action='store_true',
                        help="copy source niftis to destination using symlinks/aliases")
    parser.add_argument('--no-symlink', dest='symlink', action='store_false',
                        help="(deep) copy source niftis to destination")
    for modality_option in ["t1", "t2", "flair", "pd"]:
        # each --x-labels argument can be a list e.g. --t1-labels a b c
        # https://stackoverflow.com/a/15753721/2624391
        parser.add_argument('--%s-labels' % (modality_option), nargs='+', help='%s labels' % (modality_option.upper()))
    parser.add_argument('sub', type=str, help='sub command')
    args = parser.parse_args()

    if args.sub == 'create':
        if not args.p:
            raise ValueError("Must specify -p path to directory of Niftis")
        create(args)
    else:
        raise ValueError("unrecognized sub-command, " + args.sub)


if __name__ == "__main__":
    main()
