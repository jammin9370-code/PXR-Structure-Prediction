#Smart Pose Selector

import os
from pathlib import Path
from collections import defaultdict

print("🚑 SURGICAL INTERVENTION ON REBEL COMPOUNDS (Top 2 Extraction)...")

ribelli = ["x02828-1", "x03421-1"]
cartella_sdf = Path("Risultati_Gnina_PXR")
cartella_out = Path("Complessi_Numerati_PDB")
file_recettore = "receptor_PXR.pdb"

linee_recettore = []
ultima_riga_atom = ""
indice_ter = 0

with open(file_recettore, "r") as f:
    for line in f:
        if line.startswith("ATOM"):
            linee_recettore.append(line)
            ultima_riga_atom = line
            indice_ter = int(line[6:11].strip()) + 1

riga_ter = f"TER   {indice_ter:>5}      {ultima_riga_atom[17:20]} {ultima_riga_atom[21]}{ultima_riga_atom[22:26]}\n"

for nome in ribelli:
    file_sdf = cartella_sdf / f"{nome}_docked.sdf"
    file_out = cartella_out / f"{nome}.pdb"
    if not file_sdf.exists(): continue
        
    with open(file_sdf, "r") as f: contenuto = f.read()
    pose_sdf = [p + "$$$$\n" for p in contenuto.split("$$$$\n") if p.strip()]
    posa_da_usare = pose_sdf[1] if len(pose_sdf) >= 2 else pose_sdf[0]
        
    with open("temp.sdf", "w") as f: f.write(posa_da_usare)
    os.system("obabel -isdf temp.sdf -opdb -O temp_lig.pdb -d 2> NUL")
    
    if not os.path.exists("temp_lig.pdb"): continue
        
    linee_lig_formattate = []
    contatori_elementi = defaultdict(int)
    idx_ligando = indice_ter + 1
    
    with open("temp_lig.pdb", "r") as f:
        for line in f:
            if line.startswith("ATOM") or line.startswith("HETATM"):
                atom_name_orig = line[12:16].strip()
                if atom_name_orig.startswith("H") or (len(atom_name_orig)>1 and atom_name_orig[1]=="H" and atom_name_orig[0].isdigit()):
                    continue
                x, y, z = float(line[30:38]), float(line[38:46]), float(line[46:54])
                elemento = atom_name_orig[0].upper()
                if len(atom_name_orig) > 1 and atom_name_orig[:2].upper() in ["CL", "BR", "FE", "MG", "ZN", "NA", "CU", "SI"]:
                    elemento = atom_name_orig[:2].upper()
                contatori_elementi[elemento] += 1
                nuovo_nome = f"{elemento}{contatori_elementi[elemento]}"
                atom_formatted = f" {nuovo_nome:<3}" if len(nuovo_nome) < 4 else nuovo_nome[:4]
                linee_lig_formattate.append(f"HETATM{idx_ligando:>5} {atom_formatted} LIG B   1    {x:>8.3f}{y:>8.3f}{z:>8.3f}  1.00 20.00          {elemento:>2}\n")
                idx_ligando += 1
                
    with open(file_out, "w") as f:
        f.writelines(linee_recettore)
        f.write(riga_ter)
        f.writelines(linee_lig_formattate)
        f.write("END\n")
    print(f"✅ {nome} overwritten with Top 2 pose!")

if os.path.exists("temp.sdf"): os.remove("temp.sdf")
if os.path.exists("temp_lig.pdb"): os.remove("temp_lig.pdb")
