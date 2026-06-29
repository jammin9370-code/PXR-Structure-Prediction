#Complex Generation and TER Record Insertion

import glob
from pathlib import Path
from collections import defaultdict

print("🔢 STARTING LIGAND RENUMBERING AND 'TER' INSERTION...")

cartella_in = Path("Complessi_Finali_PDB")
cartella_out = Path("Complessi_Numerati_PDB")
cartella_out.mkdir(exist_ok=True)

file_pdb_disponibili = glob.glob(str(cartella_in / "*.pdb"))
conteggio = 0

for file_pdb in file_pdb_disponibili:
    nome_file = Path(file_pdb).name
    with open(file_pdb, "r") as f:
        lines = f.readlines()
        
    linee_finali = []
    contatori_elementi = defaultdict(int)
    inserito_ter = False
    indice_corrente = 0
    ultima_riga_atom = ""
    
    for line in lines:
        if line.startswith("ATOM"):
            linee_finali.append(line)
            ultima_riga_atom = line
            try: indice_corrente = int(line[6:11].strip())
            except ValueError: pass
        elif line.startswith("HETATM") and "LIG" in line:
            if not inserito_ter:
                indice_ter = indice_corrente + 1
                if ultima_riga_atom:
                    res_name = ultima_riga_atom[17:20]
                    chain = ultima_riga_atom[21]
                    res_seq = ultima_riga_atom[22:26]
                    riga_ter = f"TER   {indice_ter:>5}      {res_name} {chain}{res_seq}\n"
                else:
                    riga_ter = f"TER   {indice_ter:>5}\n"
                linee_finali.append(riga_ter)
                inserito_ter = True
                indice_corrente = indice_ter
            
            indice_corrente += 1
            atom_name_orig = line[12:16].strip()
            elemento = atom_name_orig[0].upper()
            if len(atom_name_orig) > 1 and atom_name_orig[:2].upper() in ["CL", "BR", "FE", "MG", "ZN", "NA", "CU", "SI"]:
                elemento = atom_name_orig[:2].upper()
                
            contatori_elementi[elemento] += 1
            nuovo_nome = f"{elemento}{contatori_elementi[elemento]}"
            atom_formatted = f" {nuovo_nome:<3}" if len(nuovo_nome) < 4 else nuovo_nome[:4]
            nuova_linea = f"{line[:6]}{indice_corrente:>5} {atom_formatted}{line[16:]}"
            linee_finali.append(nuova_linea)
        else:
            linee_finali.append(line)
            
    with open(cartella_out / nome_file, "w") as f:
        f.writelines(linee_finali)
    conteggio += 1

print(f"🎉 DONE! {conteggio} files saved in '{cartella_out}'.")
