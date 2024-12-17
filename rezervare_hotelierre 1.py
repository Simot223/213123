import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import json
# Clasele
class Camera:
   def __init__(self, numar, tip, pret_pe_noapte):
       self.numar = numar
       self.tip = tip
       self.pret_pe_noapte = pret_pe_noapte
       self.este_disponibila = True
   def rezervare(self):
       self.este_disponibila = False
   def eliberare(self):
       self.este_disponibila = True
   def modifica_pret(self, noul_pret):
       self.pret_pe_noapte = noul_pret

class Client:
   def __init__(self, nume, telefon):
       self.nume = nume
       self.telefon = telefon

class Rezervare:
   def __init__(self, client, camera, data_inceput, data_sfarsit):
       self.client = client
       self.camera = camera
       self.data_inceput = datetime.strptime(data_inceput, "%Y-%m-%d")
       self.data_sfarsit = datetime.strptime(data_sfarsit, "%Y-%m-%d")
       self.camera.rezervare()
       self.pret_total = self.calculeaza_pret_total()
   def calculeaza_pret_total(self):
       durata = (self.data_sfarsit - self.data_inceput).days
       if durata < 1:
           return self.camera.pret_pe_noapte  # Dacă este selectată doar o noapte
       return durata * self.camera.pret_pe_noapte

class Hotel:
   def __init__(self, nume):
       self.nume = nume
       self.camere = []
       self.rezervari = []
   def adauga_camera(self, camera):
       self.camere.append(camera)
   def listeaza_camere_disponibile(self):
       return [camera for camera in self.camere if camera.este_disponibila]
   def fa_rezervare(self, client, numar_camera, data_inceput, data_sfarsit):
       camera = next((c for c in self.camere if c.numar == numar_camera and c.este_disponibila), None)
       if camera:
           rezervare = Rezervare(client, camera, data_inceput, data_sfarsit)
           self.rezervari.append(rezervare)
           return rezervare.pret_total  # Rambursăm prețul integral
       else:
           return None
   def anuleaza_rezervare(self, numar_camera):
       rezervare = next((r for r in self.rezervari if r.camera.numar == numar_camera), None)
       if rezervare:
           rezervare.camera.eliberare()
           self.rezervari.remove(rezervare)
           return f"Rezervarea pentru camera {numar_camera} a fost anulată."
       else:
           return "Nu există o rezervare pentru această cameră."
   def modifica_pret_camera(self, numar_camera, noul_pret):
       camera = next((c for c in self.camere if c.numar == numar_camera), None)
       if camera:
           camera.modifica_pret(noul_pret)
           return f"Prețul pentru camera {numar_camera} a fost modificat la {noul_pret} RON/noapte."
       else:
           return "Camera nu a fost găsită."
   def salveaza_in_fisier(self, filename="hotel_data.json"):
       # Salvarea stării într-un fișier 
       data = {
           "camere": [{
               "numar": c.numar,
               "tip": c.tip,
               "pret_pe_noapte": c.pret_pe_noapte,
               "este_disponibila": c.este_disponibila
           } for c in self.camere],
           "rezervari": [{
               "client": {
                   "nume": r.client.nume,
                   "telefon": r.client.telefon
               },
               "camera": r.camera.numar,
               "data_inceput": r.data_inceput.strftime("%Y-%m-%d"),
               "data_sfarsit": r.data_sfarsit.strftime("%Y-%m-%d"),
               "pret_total": r.pret_total
           } for r in self.rezervari]
       }
       with open(filename, "w") as f:
           json.dump(data, f)
   def incarca_din_fisier(self, filename="hotel_data.json"):
       try:
           with open(filename, "r") as f:
               data = json.load(f)
               self.camere = [Camera(c["numar"], c["tip"], c["pret_pe_noapte"]) for c in data["camere"]]
               self.rezervari = [Rezervare(
                   Client(r["client"]["nume"], r["client"]["telefon"]),
                   next(c for c in self.camere if c.numar == r["camera"]),
                   r["data_inceput"], r["data_sfarsit"]
               ) for r in data["rezervari"]]
       except FileNotFoundError:
           pass  # Dacă fișierul nu este găsit, omiteți-l

# Crearea unui hotel și adăugarea de camere
hotel = Hotel("Hotelul Luminița")
camere = [Camera(f"a{i+1}", "Single", 150) for i in range(3)] + \
        [Camera(f"b{i+1}", "Double", 250) for i in range(3)] + \
        [Camera(f"c{i+1}", "Suite", 300) for i in range(3)]
for camera in camere:
   hotel.adauga_camera(camera)
# Încărcarea datelor dintr-un fișier
hotel.incarca_din_fisier()
# Funcții GUI
def show_available_rooms():
   rooms = hotel.listeaza_camere_disponibile()
   if rooms:
       room_details = "\n".join([f"Camera {camera.numar} ({camera.tip}) - {camera.pret_pe_noapte} RON/noapte"
                                for camera in rooms])
       messagebox.showinfo("Camere disponibile", room_details)
   else:
       messagebox.showinfo("Camere disponibile", "Nu sunt camere disponibile.")
def reserve_room():
   nume = name_entry.get()
   telefon = phone_entry.get()
   numar_camera = room_entry.get()
   data_inceput = start_date_entry.get()
   data_sfarsit = end_date_entry.get()
   if not (nume and telefon and numar_camera and data_inceput and data_sfarsit):
       messagebox.showwarning("Eroare", "Toate câmpurile trebuie completate!")
       return
   client = Client(nume, telefon)
   pret_total = hotel.fa_rezervare(client, numar_camera, data_inceput, data_sfarsit)
   if pret_total:
       messagebox.showinfo("Rezervare", f"Rezervarea realizată cu succes!\nPreț total: {pret_total} RON")
   else:
       messagebox.showwarning("Eroare", "Camera nu este disponibilă.")
def cancel_reservation():
   numar_camera = room_entry.get()
   if not numar_camera:
       messagebox.showwarning("Eroare", "Introduceți numărul camerei!")
       return
   mesaj = hotel.anuleaza_rezervare(numar_camera)
   messagebox.showinfo("Anulare rezervare", mesaj)
def change_room_price():
   def update_price():
       numar_camera = camera_number_entry.get()
       try:
           noul_pret = float(new_price_entry.get())
           mesaj = hotel.modifica_pret_camera(numar_camera, noul_pret)
           messagebox.showinfo("Modificare preț", mesaj)
           price_window.destroy()  # Închideți fereastra după actualizarea prețului
       except ValueError:
           messagebox.showwarning("Eroare", "Introduceti un preț valid!")
   price_window = tk.Toplevel(root)
   price_window.title("Modifică prețul camerei")
   price_window.geometry("400x200")
   tk.Label(price_window, text="Numărul camerei:", font=("Arial", 12)).pack(pady=10)
   camera_number_entry = tk.Entry(price_window, font=("Arial", 12))
   camera_number_entry.pack(pady=5)
   tk.Label(price_window, text="Noua preț (RON/noapte):", font=("Arial", 12)).pack(pady=10)
   new_price_entry = tk.Entry(price_window, font=("Arial", 12))
   new_price_entry.pack(pady=5)
   tk.Button(price_window, text="Modifică prețul", command=update_price).pack(pady=20)
# Crearea unei ferestre GUI
root = tk.Tk()
root.title("Sistem de Rezervare Hotelier")
root.geometry("600x400")  # Setarea dimensiunii ferestrei
root.config(bg="green")  # Fundal verde pentru întreaga fereastră
# Crearea elementelor de interfață
tk.Label(root, text="Nume:", font=("Arial", 12), bg="green").pack(pady=10)
name_entry = tk.Entry(root, font=("Arial", 12))
name_entry.pack(pady=5)
tk.Label(root, text="Telefon:", font=("Arial", 12), bg="green").pack(pady=10)
phone_entry = tk.Entry(root, font=("Arial", 12))
phone_entry.pack(pady=5)
tk.Label(root, text="Numar camera:", font=("Arial", 12), bg="green").pack(pady=10)
room_entry = tk.Entry(root, font=("Arial", 12))
room_entry.pack(pady=5)
tk.Label(root, text="Data inceput (YYYY-MM-DD):", font=("Arial", 12), bg="green").pack(pady=10)
start_date_entry = tk.Entry(root, font=("Arial", 12))
start_date_entry.pack(pady=5)
tk.Label(root, text="Data sfarsit (YYYY-MM-DD):", font=("Arial", 12), bg="green").pack(pady=10)
end_date_entry = tk.Entry(root, font=("Arial", 12))
end_date_entry.pack(pady=5)
# Butoane
tk.Button(root, text="Arata camere disponibile", font=("Arial", 12), command=show_available_rooms).pack(pady=10)
tk.Button(root, text="Rezerva camera", font=("Arial", 12), command=reserve_room).pack(pady=10)
tk.Button(root, text="Anuleaza rezervare", font=("Arial", 12), command=cancel_reservation).pack(pady=10)
tk.Button(root, text="Modifica pret camera", font=("Arial", 12), command=change_room_price).pack(pady=10)
root.mainloop()
# Salveaza datele dupa ce se incide aplicatia
hotel.salveaza_in_fisier()


