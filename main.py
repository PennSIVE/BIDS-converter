import argparse
import pathlib
import shutil
import glob
import csv
import re
import os


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
            session = p[p.find(before_session)+len(before_session):p.find(after_session)]
        if args.m:
            modality = args.m.upper()
        else:
            modality = p[p.find(before_modality)+len(before_modality):p.find(after_modality)].upper()
            if 'T1' in modality:
                modality = 'T1w'
            elif 'T2' in modality:
                modality = 'T2w'
            elif 'FLAIR' in modality:
                modality = 'FLAIR'
            elif 'PD' in modality:
                modality = 'PD'
            else:
                raise ValueError("Unrecognized modality '%s'" % (modality))
        pathlib.Path("/output/sub-"+subj+"/ses-"+session +
                     "/anat").mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, "/output/sub-"+subj+"/ses-"+session+"/anat/sub-" +
                        subj+"_ses-"+session+"_run-001_"+modality+".nii.gz")
        with open("/output/sub-"+subj+"/ses-"+session+"/anat/sub-"+subj+"_ses-"+session+"_run-001_"+modality+".json", 'w') as f:
            f.write("{}")
        with open("/output/sub-"+subj+"/ses-"+session+"/anat/sub-"+subj+"_ses-"+session+"_scans.json", 'w') as f:
            f.write("{}")
        with open("/output/sub-"+subj+"/ses-"+session+"/sub-"+subj+"_ses-"+session+"_scans.tsv", 'w') as f:
            writer = csv.writer(f, delimiter='\t')
            if not f.readable():
                writer.writerow(['filename', 'acq_time'])
            writer.writerow(
                ['anat/' + os.path.basename(p), '1970-01-01T00:00:00'])

    # other req'd BIDS meta data
    with open('/output/dataset_description.json', 'w') as f:
        f.write('{"Acknowledgements":"TODO: whom you want to acknowledge","Authors":["TODO:","First1 Last1","First2 Last2","..."],"BIDSVersion":"1.0.1","DatasetDOI":"TODO: eventually a DOI for the dataset","Funding":["TODO","GRANT #1","GRANT #2"],"HowToAcknowledge":"TODO: describe how to acknowledge -- either cite a corresponding paper, or just in acknowledgement section","License":"TODO: choose a license, e.g. PDDL (http://opendatacommons.org/licenses/pddl/)","Name":"TODO: name of the dataset","ReferencesAndLinks":["TODO","List of papers or websites"]}')
    with open('/output/participants.json', 'w') as f:
        f.write("{}")
    with open('/output/README', 'w') as f:
        f.write("TODO")
    with open('/output/participants.tsv', 'w') as f:
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
