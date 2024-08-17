import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import sqlite3
import pandas as pd
import threading
# from PIL import Image, ImageTk
import sys, os

# import ctypes

# db_location = r"soil.db"
db_locations = [r"\\labsrv2012\soil_database\soil.db", r"\\192.168.1.217\soil_database\soil.db"]
#db_locations = [r"\\Cetfileserver\all_users\Suman Atta\soil.db", r"\\192.168.0.220\all_users\Suman Atta\soil.db"]

# db_locations = [r"soil.db"]




# once connection is estabilished, delete other database location to faster data access    
for db_location in db_locations:
    try:
        conn = sqlite3.connect(db_location)
        c = conn.cursor()
        
        db_locations = [db_location]
        break
    except sqlite3.Error as e:
        
        continue




##Check If database is available

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



# Define main application class
class SoilReportApp:
    def __init__(self, root):
        



        self.root = root
        self.root.geometry("850x700")
        self.root.title("Soil Report Application")

        
        style = ttk.Style()
        style.configure("TLabel", font=("Helvetica", 12), padding=5, background="#E0E0E0", foreground="#4169E1")
        style.configure("TEntry", font=("Helvetica", 12,), padding=5, fieldbackground="#F0F0F0", foreground="#4169E1")
        style.configure("TButton", font=("Helvetica", 12, "bold"), padding=1, background="#4682B4", foreground="#4169E1", relief="raised")
        style.map("TButton", background=[('active', '#5A9BD3'), ('hover', '#ADD8E6')], foreground=[('active', '#000000'), ('hover', '#000000')])
        style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), padding=5, background="#4682B4", foreground="#FFFFFF")
        style.configure("Desc.TEntry", font=("Helvetica", 12), padding=5, fieldbackground="#F0F0F0", foreground="#4169E1")
        style.configure("TFrame", background="#D3D3D3")

        # For the 'hover' state to work, the 'TButton' style must be applied as below
        style.map("TButton",
            background=[('!active', '#4682B4'), ('hover', '#ADD8E6'), ('pressed', '#5A9BD3')],
            foreground=[('!active', '#4169E1'), ('hover', '#000000'), ('pressed', '#FFFFFF')]
        )

        style.configure("TNotebook.Tab", font=("Helvetica", 10, "bold"), padding=[8, 5], background="#4682B4", foreground="#016d93")
        style.map("TNotebook.Tab", background=[("selected", "#4169E1")], foreground=[("selected", "#4169E1")])









        # Header Label
        header = ttk.Label(root, text="Soil Report Application", font=("Helvetica", 16, "bold"), background="")
        header.pack(pady=10)

        # Create notebook (tabs container)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=1, fill='both', padx=15, pady=15)

        # Create tabs
        self.create_sample_tab = ttk.Frame(self.notebook)
        self.generate_report_tab = ttk.Frame(self.notebook)
        self.update_tab = ttk.Frame(self.notebook)

        # Add tabs to the notebook
        self.notebook.add(self.create_sample_tab, text='Create Sample')
        self.notebook.add(self.generate_report_tab, text='Generate Report')
        self.notebook.add(self.update_tab, text='Update')

        def rebind_enter(event=None):
            current_tab = self.notebook.index(self.notebook.select())
            if current_tab == 0:
                root.bind('<Return>', lambda e: save_new_record())
            elif current_tab == 1:
                root.bind('<Return>', lambda e: view_report())
            elif current_tab == 2:
                root.bind('<Return>', lambda e: search_action())

        # Bind the <<NotebookTabChanged>> event to call rebind_enter
        self.notebook.bind('<<NotebookTabChanged>>', rebind_enter)

    # Call rebind_enter initially to set the binding based on the default tab
        rebind_enter()

        # Add content to each tab
        self.add_create_sample_content()
        self.add_generate_report_content()
        self.add_update_content()

        # Create the bottom frame
        self.bottom_frame = ttk.Frame(root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        # Add initial content to the bottom frame
        # self.bottom_label = ttk.Label(self.bottom_frame, text="Select a tab to load content here")
        # self.bottom_label.pack()

        # Bind tab change event
        #self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Resize and display image
        # image_path = resource_path("Logo.png")

        # image = Image.open(image_path)
        # photo = ImageTk.PhotoImage(image)

        # # Use regular Tkinter Label for the image
        # self.image_label = tk.Label(root, image=photo)
        # self.image_label.image = photo  # Keeping a reference
        # self.image_label.pack(pady=5)

    def add_create_sample_content(self):
        global save_new_record

        # Create StringVar instances for entry fields
        job_no_var = tk.StringVar()
        bh_loc_var = tk.StringVar()
        sample_no_var = tk.StringVar()
        depth_var = tk.StringVar()
        project_name_var = tk.StringVar()
        desc_var = tk.StringVar()

        def clear_entries():
            bh_loc_var.set("")
            sample_no_var.set("")
            depth_var.set("")
            # project_name_var.set("")
            # desc_var.set("")

        def is_null_or_empty(*args):
            for arg in args:
                if arg is None or arg == "":
                    return True
            return False

        def check_job_number(event):
            job_no = job_no_var.get().strip()
            if not job_no:
                return

            try:
                conn, c = connect_to_database(db_locations)
                #used LIMIT clause beacuse there may be more than one same job number and project name
                # always remains same with a job number so, it will work fine
                c.execute("SELECT Project FROM soil WHERE job_no = ? LIMIT 1", (job_no,))
                result = c.fetchone()

                #If existing job number found on database then use existng project name always, and restrict user from changing the project name
                if result:
                    project_name_var.set(result[0])
                    project_name_entry.config(state='readonly')
                else:
                    project_name_var.set('')
                    project_name_entry.config(state='normal')

            except sqlite3.Error as e:
                messagebox.showerror("Error!", f"Error while connecting to the database\n{e}")

            finally:
                if conn:
                    conn.close()

        def save_new_record():
            if is_null_or_empty(job_no_var.get(), bh_loc_var.get(), sample_no_var.get(), depth_var.get(), project_name_var.get(), desc_var.get()):
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            try:
                x = float(depth_var.get())
            except:
                messagebox.showerror("Error", "Depth must be a number")
                return

            confirmed = messagebox.askyesno("Confirm Save", "Are you sure you want to save the new record?")
            if not confirmed:
                return

            try:
                conn, c = connect_to_database(db_locations)
                c.execute("SELECT uid FROM soil WHERE job_no = ? AND Bore_Hole = ? AND sample_no = ?", 
                        (job_no_var.get().strip(), bh_loc_var.get().strip(), sample_no_var.get().strip()))
                result = c.fetchone()

                if result:
                    messagebox.showerror("Duplicate Entry", "Record Already Exists. Please verify inputs.")
                else:
                    c.execute(
                        "INSERT INTO soil (job_no, Bore_Hole, sample_no, depth, Project, Desc1) VALUES (?, ?, ?, ?, ?, ?)",
                        (job_no_var.get().strip(), bh_loc_var.get().strip(), sample_no_var.get().strip(), depth_var.get().strip(), project_name_var.get().strip(), desc_var.get().strip()))

                    if c.rowcount == 1:
                        conn.commit()
                        messagebox.showinfo("Success!", "New Record created successfully")
                        clear_entries()
                        project_name_entry.config(state='normal')
                    else:
                        messagebox.showinfo("Error!", "Failed to insert the new record")

            except sqlite3.Error as e:
                messagebox.showerror("Error!", f"Error while connecting to the database\n{e}")

            finally:
                if conn:
                    conn.close()

        # Frame for form
        frame = ttk.Frame(self.create_sample_tab, padding=(20, 20, 20, 20))
        frame.grid(row=0, column=0, sticky="nsew")

        # Header
        header_label = ttk.Label(frame, text="New Sample Entry", style="Header.TLabel")
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Create labels and entry fields
        fields = [
            ("Job No:", job_no_var),
            ("Project Name:", project_name_var),
            ("BH-Location:", bh_loc_var),
            ("Sample No.:", sample_no_var),
            ("Depth:", depth_var),
            ("Description:", desc_var)
        ]

        entry_widgets = []
        for i, (label_text, var) in enumerate(fields):
            label = ttk.Label(frame, text=label_text, style="TLabel")

            width = 40 if label_text == "Project Name:" else 80 if label_text == "Description:" else 20

            entry = ttk.Entry(frame, textvariable=var, style="TEntry", width=width)

            # Check if job number alreday exist or not
            if label_text == "Job No:":
                entry.bind('<FocusOut>', check_job_number)

            label.grid(row=i + 1, column=0, padx=5, pady=5, sticky='e')
            entry.grid(row=i + 1, column=1, padx=5, pady=5, sticky='w')
            entry_widgets.append(entry)

        # Store the project name entry widget for later use
        project_name_entry = entry_widgets[1]

        # Create button
        save_btn = ttk.Button(frame, text="Save", style="TButton", command=save_new_record)
        cancel_btn = ttk.Button(frame, text="Cancel", style="TButton", command=self.root.destroy)
        save_btn.grid(row=len(fields) + 1, column=0, padx=5, pady=10, sticky='e')
        cancel_btn.grid(row=len(fields) + 1, column=1, padx=5, pady=10, sticky='w')

        # Ensure the frame expands to fill the window
        self.create_sample_tab.grid_columnconfigure(0, weight=1)
        self.create_sample_tab.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    def add_generate_report_content(self):
        global view_report

        def fetch_job_no():
            # conn = sqlite3.connect(db_location)
            conn,c = connect_to_database(db_locations)
            cursor = conn.cursor()

            
            query = "SELECT DISTINCT job_no FROM soil"
            cursor.execute(query)
            values = [row[0] for row in cursor.fetchall()]
            conn.close()
            return values 

        def generate_report():
            job_no = job_combo_box.get()
            if not job_no:
                messagebox.showerror("Input Error", "Please select a job number.")
                return

            def generate():
                # conn = sqlite3.connect(db_location)
                conn,c = connect_to_database(db_locations)
                cursor = conn.cursor()
                query = "SELECT * FROM soil WHERE job_no = ? ORDER BY Bore_Hole ASC, depth ASC"
                cursor.execute(query, (job_no,))
                rows = cursor.fetchall()

                # Fetch column names excluding 'uid'
                cursor.execute("PRAGMA table_info(soil)")
                columns_info = cursor.fetchall()
                columns = [info[1] for info in columns_info if info[1] != 'uid']

                conn.close()

                if rows:
                    # Adjust rows to match the column names by excluding the last 'uid' field
                    rows = [row[:-1] for row in rows]  # Exclude the 'uid' field from each row
                    
                    #Rounding Up some values. 
                    #Converting into list of lists because tuple does not support item assignment


                    rows = [list(item) for item in rows]
                    for row in rows:
                        if isinstance(row[4],float):
                            row[4] = f"{row[4]:.2f}"
                            
                        #BD
                        if isinstance(row[8],float):
                            row[8] = round(row[8],2)
                            #DD
                        if isinstance(row[9],float):
                            row[9] = round(row[9],2)

                            #NMC
                        if isinstance(row[10],float):
                            row[10] = round(row[10],0)
                            #SPG
                        if isinstance(row[16],float):
                            row[16] = round(row[16],2)
                            #VOID RATIO 3
                        if isinstance(row[17],float):
                            row[17] = round(row[17],3)
                            #FRI
                        if isinstance(row[47],float):
                            row[47] = round(row[47],0)
                        if isinstance(row[49],float):
                            row[49] = round(row[49],0)
                        if isinstance(row[51],float):
                            row[51] = round(row[51],0)
                        if isinstance(row[53],float):
                            row[53] = round(row[53],0)
                            #LL
                        if isinstance(row[54],float):
                            row[54] = round(row[54],0)
                            #PL
                        if isinstance(row[55],float):
                            row[55] = round(row[55],0)
                            #SL
                        if isinstance(row[61],float):
                            row[61] = round(row[61],0)
                            #STRN
                        if isinstance(row[23],float):
                            row[23] = round(row[23],3)
                        if isinstance(row[25],float):
                            row[25] = round(row[25],3)
                        if isinstance(row[27],float):
                            row[27] = round(row[27],3)
                        if isinstance(row[29],float):
                            row[29] = round(row[29],3)
                        if isinstance(row[31],float):
                            row[31] = round(row[31],3)
                        if isinstance(row[33],float):
                            row[33] = round(row[33],3)
                        if isinstance(row[35],float):
                            row[35] = round(row[35],3)
                        if isinstance(row[37],float):
                            row[37] = round(row[37],3)
                        if isinstance(row[39],float):
                            row[39] = round(row[39],3)
                        if isinstance(row[41],float):
                            row[41] = round(row[41],3)
                        if isinstance(row[43],float):
                            row[43] = round(row[43],3)
                        if isinstance(row[45],float):
                            row[45] = round(row[45],3)
                            #COHE
                        if isinstance(row[46],float):
                            row[46] = round(row[46],2)
                        if isinstance(row[48],float):
                            row[48] = round(row[48],2)
                        if isinstance(row[50],float):
                            row[50] = round(row[50],2)
                        if isinstance(row[52],float):
                            row[52] = round(row[52],2)
                        
                        if isinstance(row[11],float):
                            row[11] = round(row[11],0)
                            #gravel
                        if isinstance(row[59],float) or isinstance(row[59],int):
                            if row[59] == 0:
                                row[59] = None
                            
                        

                    # Create DataFrame
                    df = pd.DataFrame(rows, columns=columns)
                    df.insert(0, '', '')

                    # Save DataFrame to Excel file
                    filename = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                            initialfile=f"{job_combo_box.get()}.xlsx",
                                                            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
                    if filename:
                        df.to_excel(filename, index=False)
                        messagebox.showinfo("Success", "Report generated successfully!")
                else:
                    messagebox.showinfo("No Data", "No records found for the selected job number.")

                # progress_bar.stop()

            # progress_bar.start()
            threading.Thread(target=generate).start()

        def view_report():
            job_no = job_combo_box.get()
            if not job_no:
                messagebox.showerror("Input Error", "Please select a job number.")
                return

            data = fetch_data(job_no)
            data = [list(item) for item in data]
            # print(data)
            for row in data:
                if isinstance(row[2],float):
                    row[2] = f"{row[2]:.2f}"
            if data:
                show_data_window(data,job_no)
            else:
                messagebox.showinfo("No Data", "No records found for the selected job number.")

        def fetch_data(job_no):
            try:
                # conn = sqlite3.connect(db_location)
                conn, c = connect_to_database(db_locations)
                cursor = conn.cursor()
                query = """
                SELECT Bore_Hole, sample_no, depth, Test_Type1, Test_Type2, Test_Type3, Test_Type4, bulk_density, NMC, LL, PL, SL, VREO18, sand, clay, SPG 
                FROM soil 
                WHERE job_no = ? 
                ORDER BY Bore_Hole ASC, depth ASC
                """
                cursor.execute(query, (job_no,))
                data = cursor.fetchall()
                conn.close()
                return data
            except Exception as e:
                messagebox.showerror("Database Error", str(e))
                return None

        def show_data_window(data, jobNo):
            data_window = tk.Toplevel(self.root)
            data_window.title(f"Preview Report for Job No: {jobNo}")

            columns = ["BH Loc.", "Sample No", "Depth", "TRSH-UU", "UNCONFD", "REMOULD", "DRSH-CQ", "BD", "NMC", "LL", "PL", "SL", "Void Ratio", "Sieve", "HYD", "SPG"]
            tree = ttk.Treeview(data_window, columns=columns, show='headings')

            # Style the Treeview
            style = ttk.Style()
            style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"), background="white", foreground="#4682b4")
            style.configure("Treeview", font=("Helvetica", 10), rowheight=25)
            style.map("Treeview", background=[("selected", "#ADD8E6")], foreground=[("selected", "black")])

            # Create headings with styling
            for col in columns:
                tree.heading(col, text=col, anchor=tk.CENTER)
                tree.column(col, anchor=tk.CENTER, width=70)
            
            # Define tags for alternate row colors
            tree.tag_configure('oddrow', background='#cce8ed')
            tree.tag_configure('evenrow', background='#ffffff')

            # Insert data rows
            for idx, row in enumerate(data):
                sanitized_row = ["" if ele is None or ele == "" else "✓" if idx >= 3 else ele for idx, ele in enumerate(row)]
                tag = 'oddrow' if idx % 2 == 0 else 'evenrow'
                tree.insert("", tk.END, values=sanitized_row, tags=(tag,))

            # Add scrollbar
            scrollbar = ttk.Scrollbar(data_window, orient="vertical", command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            tree.pack(fill=tk.BOTH, expand=True)

            # Ensure the headers are visible
            tree.pack(fill=tk.BOTH, expand=True)
            data_window.update_idletasks()

        # Frame for Generate Report tab content
        frame = ttk.Frame(self.generate_report_tab, padding=(20, 20, 20, 20))
        frame.grid(row=0, column=0, sticky="nsew")

        # Header
        header_label = ttk.Label(frame, text="Generate Report", style="Header.TLabel")
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Job Number ComboBox
        job_label = ttk.Label(frame, text="Job No:", style="TLabel")
        job_combo_box = ttk.Combobox(frame, values=fetch_job_no(), style="TEntry", width=30)
        job_combo_box.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        job_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        def update_combobox_values():
            job_combo_box['values'] = fetch_job_no()

        # Generate Button
        generate_btn = ttk.Button(frame, text="Generate", style="TButton", command=generate_report)
        generate_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=10)

        # View Button
        view_btn = ttk.Button(frame, text="View", style="TButton", command=view_report)
        view_btn.grid(row=2, column=1, columnspan=2, padx=5, pady=10)

        refresh_btn = ttk.Button(frame, text="Refresh", style="TButton", command=update_combobox_values)
        refresh_btn.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # frame.bind('<Return>', lambda event: view_report())

        # Ensure the frame expands to fill the window
        self.generate_report_tab.grid_columnconfigure(0, weight=1)
        self.generate_report_tab.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)


    def add_update_content(self):
        global search_action

        def fetch_values(query, params=()):
            # conn = sqlite3.connect(db_location)
            conn,c = connect_to_database(db_locations)
            cursor = conn.cursor()
            cursor.execute(query, params)
            values = [row[0] for row in cursor.fetchall()]
            conn.close()
            return values

        def fetch_record(job_no, bh_loc, sample_no):
            # conn = sqlite3.connect(db_location)
            conn,c = connect_to_database(db_locations)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM soil WHERE job_no = ? AND Bore_Hole = ? AND sample_no = ?", (job_no, bh_loc, sample_no))
            record = cursor.fetchone()
            conn.close()
            return record

        def update_record(job_no, bh_loc, sample_no, new_values):
            # conn = sqlite3.connect(db_location)
            conn,c = connect_to_database(db_locations)
            cursor = conn.cursor()
            fields = ", ".join([f"{field} = ?" for field in new_values.keys()])
            values = list(new_values.values())
            uid = cursor.execute("SELECT uid FROM soil WHERE job_no = ? AND Bore_Hole = ? AND sample_no = ?", (job_no, bh_loc, sample_no)).fetchone()[0]
            values.append(uid)  # Append uid to values
            cursor.execute(f"UPDATE soil SET {fields} WHERE uid = ?", tuple(values))  # Pass values as a tuple
            conn.commit()
            conn.close()


        # Search Frame
        search_frame = ttk.Frame(self.update_tab)
        search_frame.pack(pady=10)
        # header_label = ttk.Label(search_frame, text="Update", style="Header.TLabel")
        # header_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='e')
        job_search_label = ttk.Label(search_frame, text="Job No: ")
        job_search_label.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        bh_loc_search_label = ttk.Label(search_frame, text="BH-Location: ")
        bh_loc_search_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')

        sample_no_search_label = ttk.Label(search_frame, text="Sample No.: ")
        sample_no_search_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')

        # Fetch values for combo boxes from database
        job_nos = fetch_values("SELECT DISTINCT job_no FROM soil")

        # Create combo boxes
        job_entry_search = ttk.Combobox(search_frame, values=job_nos)
        job_entry_search.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        bh_loc_search = ttk.Combobox(search_frame)
        bh_loc_search.grid(row=1, column=1, padx=5, pady=5, sticky='w')

        sample_no_search = ttk.Combobox(search_frame)
        sample_no_search.grid(row=2, column=1, padx=5, pady=5, sticky='w')

        def update_bh_locations(event):
            job_no = job_entry_search.get()
            if job_no:
                bh_locations = fetch_values("SELECT DISTINCT Bore_Hole FROM soil WHERE job_no = ?", (job_no,))
                bh_loc_search['values'] = bh_locations
                bh_loc_search.set('')
                sample_no_search.set('')
                sample_no_search['values'] = []
        
        def update_sample_nos(event):
            job_no = job_entry_search.get()
            bh_loc = bh_loc_search.get()
            if job_no and bh_loc:
                sample_nos = fetch_values("SELECT DISTINCT sample_no FROM soil WHERE job_no = ? AND Bore_Hole = ?", (job_no, bh_loc))
                sample_no_search['values'] = sample_nos
                sample_no_search.set('')
        
        #Used Focus Out event also because if user puts job number manually then bh-locations won't update. Did also same with sample_no
        job_entry_search.bind("<<ComboboxSelected>>", update_bh_locations)
        job_entry_search.bind('<FocusOut>', update_bh_locations)
        bh_loc_search.bind("<<ComboboxSelected>>", update_sample_nos)
        bh_loc_search.bind('<FocusOut>', update_sample_nos)

        # Frame 2 with scrollbar and dynamic labels and entries (initially hidden)
        container = ttk.Frame(self.update_tab)
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        field_names = "job_no Project Bore_Hole sample_no depth Desc1 Desc2 Desc3 bulk_density dry_density NMC Tri_UU_MC cons_MC dir_MC col15 col16 SPG VREO18 Test_Type1 Test_Type2 Test_Type3 Test_Type4 PC1 STRN1 PC2 STRN2 PC3 STRN3 PC4 STRN4 PC5 STRN5 PC6 STRN6 PC7 STRN7 PC8 STRN8 PC9 STRN9 PC10 STRN10 PC11 STRN11 PC12 STRN12 COHE1 Fri1 COHE2 Fri2 COHE3 Fri3 COHE4 Fri4 LL PL sand silt clay gravel layer_no SL col63 col164".split()
        label_Names = "Job No, Project Name, BH-Location, Sample No, Depth, Desc1, Desc2, Desc3, Bulk Density, Dry Density, NMC, Tri_UU_MC, cons_MC, dir_MC, col15, col16, SPG, VREO18, Test-Type1, Test Type2, Test-Type3, Test-Type4, PC1, STRN1, PC2, STRN2, PC3, STRN3, PC4, STRN4, PC5, STRN5, PC6, STRN6, PC7, STRN7, PC8, STRN8, PC9, STRN9, PC10, STRN10, PC11, STRN11, PC12, STRN12, COHE1, Fri1, COHE2, Fri2, COHE3, Fri3, COHE4, Fri4, LL, PL, sand, silt, clay, gravel, Layer No, SL, Col63, Col64".split(",")

        entries = {}
        for i, field in enumerate(label_Names):
            row, col = divmod(i, 2)  # Arrange in two columns
            label = ttk.Label(scrollable_frame, text=field + ": ")
            label.grid(row=row, column=col*2, padx=5, pady=5, sticky='e')
            
            entry = ttk.Entry(scrollable_frame)
            entry.grid(row=row, column=col*2+1, padx=5, pady=5, sticky='w')
            
            entries[f"{field_names[i]}"] = entry

        container.pack_forget()  # Hide the container initially

        def search_action():
            job_no = job_entry_search.get()
            bh_loc = bh_loc_search.get()
            sample_no = sample_no_search.get()
            
            record = fetch_record(job_no, bh_loc, sample_no)
            
            if record:
                # Show container and populate entries with the record data
                container.pack(fill="both", expand=True, pady=10, padx=65, ipadx=10, ipady=10)
                canvas.pack(side="left", fill="both", expand=True)
                scrollbar.pack(side="right", fill="y")
                for i, field in enumerate(field_names):
                    entry = entries[field]
                    entry.delete(0, tk.END)
                    if record[i] is not None:
                        entry.insert(0, str(record[i]))
            else:
                messagebox.showwarning("No Record Found", "No record exists for the provided details.")

        def update_action():
            job_no = job_entry_search.get()
            bh_loc = bh_loc_search.get()
            sample_no = sample_no_search.get()
            confirmed = messagebox.askyesno("Confirmation", "Are you sure you want to update the record?")
            if not confirmed:
                return

            new_values = {field: str(entries[field].get()) for field in field_names}
            update_record(job_no, bh_loc, sample_no, new_values)
            messagebox.showinfo("Update Successful", "Record updated successfully.")
            container.pack_forget()

        def cancel_action():
            container.pack_forget()  # Hide the frame

        # Button to trigger search action
        search_button = ttk.Button(search_frame, text="Search", command=search_action, style='TButton')
        search_button.grid(row=3, column=0, columnspan=1, pady=10)
        def update_job_nos():
            job_entry_search['values'] = fetch_values("SELECT DISTINCT job_no FROM soil")

        refresh_button = ttk.Button(search_frame, text="Refresh", command=update_job_nos, style='TButton')
        refresh_button.grid(row=3, column=1, columnspan=1, pady=10)

        # search_frame.bind('<Return>', lambda event: search_action())

        # Update and Cancel buttons
        update_button = ttk.Button(scrollable_frame, text="Update", command=update_action, style='TButton')
        update_button.grid(row=(len(field_names) + 1) // 2, column=0, columnspan=2, pady=10)

        cancel_button = ttk.Button(scrollable_frame, text="Cancel", command=cancel_action, style='TButton')
        cancel_button.grid(row=(len(field_names) + 1) // 2, column=2, columnspan=2, pady=10)

        # Pack everything (initially hidden)
        container.pack(fill="both", expand=True, pady=10, padx=65, ipadx=10, ipady=10)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        container.pack_forget()  # Hide the container initially

        


# Main Application

#db locations is a list (not a single location). So, i created a function for connecting to the database.
def connect_to_database(db_locations):
    
    for db_location in db_locations:
        try:
            conn = sqlite3.connect(db_location)
            c = conn.cursor()
            print(db_locations)
           
            return conn, c
        except sqlite3.Error as e:
            print(f"Error connecting to {db_location}: {e}")
            continue
    return None, None

if __name__ == "__main__":
    
    conn, c = connect_to_database(db_locations)
if conn is None:
    # MessageBox = ctypes.windll.user32.MessageBoxW
    # MessageBox(None, 'Error connecting to database. Please inform IT department.', 'Error', 0)
    root = tk.Tk()  # Hide the main Tkinter window
    # root.withdraw()
    messagebox.showerror('Error', 'Error connecting to database. Please inform IT department.')
    root.destroy()
    
    sys.exit()

    

root = tk.Tk()
app = SoilReportApp(root)
root.mainloop()

