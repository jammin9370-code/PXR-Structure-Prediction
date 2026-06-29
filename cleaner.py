#PDB Repair & Sanitizer

import os
from pathlib import Path

print("🔧 STARTING PROTEIN REPAIR...")
cartella_out = Path("Complessi_Numerati_PDB")
file_da_correggere = ["x02828-1.pdb", "x03421-1.pdb"]

for nome_file in file_da_correggere:
    path_file = cartella_out / nome_file
    if not path_file.exists(): path_file = Path(nome_file)
    if not path_file.exists(): continue
        
    with open(path_file, "r") as f: lines = f.readlines()
    linee_finali = []
    
    for line in lines:
        if line.startswith("ATOM") and len(line.strip()) < 60:
            atom_id = line[6:11].strip()
            atom_name = line[12:16].strip()
            res_name = line[17:20].strip()
            chain = line[21]
            res_seq = line[22:26].strip()
            x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
            elemento = atom_name[0].upper()
            if len(atom_name) > 1 and atom_name[:2].upper() in ["CL", "BR", "FE", "MG", "ZN", "NA", "CU", "SI"]:
                elemento = atom_name[:2].upper()
            atom_formatted = f" {atom_name:<3}" if len(atom_name) < 4 else atom_name[:4]
            linea_riparata = f"ATOM  {atom_id:>5} {atom_formatted} {res_name:>3} {chain}{res_seq:>4}    {x:>8.3f}{y:>8.3f}{z:>8.3f}  1.00 20.00          {elemento:>2}\n"
            linee_finali.append(linea_riparata)
        else:
            linee_finali.append(line)
            
    with open(path_file, "w") as f: f.writelines(linee_finali)
    print(f"✅ {nome_file} column formatting restored!")

