import customtkinter as ctk
import os
import pandas as pd
from conector_db import get_db_engine
from carga_csv import load_all_csv_to_sql
from vista_sql import create_unified_view
from run import get_repeated_mruns_analysis

# Configuración de la carpeta de datos
CSV_FOLDER = 'datos' 

class MatriculaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Análisis de Matrículas GOB")
        self.geometry("600x450")
        ctk.set_appearance_mode("System")
        
        # Título
        ctk.CTkLabel(self, text="Análisis de Trayectoria Estudiantil", font=("Arial", 30, "bold")).pack(pady=20)

        # Botones y Status
        self.setup_widgets()
        
        # Chequeo inicial
        self.check_connection()

    def setup_widgets(self):
        # Frame para la Carga (Paso 1)
        self.load_frame = ctk.CTkFrame(self)
        self.load_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.load_frame, text="1. Cargar CSVs a Tablas SQL (matricula_AÑO)").pack(side="left", padx=10)
        self.load_button = ctk.CTkButton(self.load_frame, text="Cargar CSVs", command=self.action_load_data)
        self.load_button.pack(side="right", padx=10)

        # Frame para la Vista (Paso 2)
        self.view_frame = ctk.CTkFrame(self)
        self.view_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.view_frame, text="2. Crear Vista Unificada (vista_matriculas_unificada)").pack(side="left", padx=10)
        self.view_button = ctk.CTkButton(self.view_frame, text="Crear Vista", command=self.action_create_view)
        self.view_button.pack(side="right", padx=10)
        
        # Frame para el Análisis (Paso 3)
        self.analysis_frame = ctk.CTkFrame(self)
        self.analysis_frame.pack(pady=10, padx=20, fill="x")
        ctk.CTkLabel(self.analysis_frame, text="3. Ejecutar Análisis de Matrículas Cruzadas").pack(side="left", padx=10)
        self.analyze_button = ctk.CTkButton(self.analysis_frame, text="Ejecutar Análisis", command=self.action_run_analysis)
        self.analyze_button.pack(side="right", padx=10)
        
        # Área de Mensajes
        self.status_label = ctk.CTkLabel(self, text="Estado: Inicializando...", fg_color="transparent", wraplength=550)
        self.status_label.pack(pady=20)
        
    def check_connection(self):
        """Verifica la conexión al inicio."""
        if get_db_engine():
            self.status_label.configure(text="Estado: Conexión DB OK. Listo para cargar datos.", text_color="green")
        else:
            self.status_label.configure(text="Estado: ERROR DE CONEXIÓN. Revisa conector_db.py y el driver ODBC.", text_color="red")
            self.load_button.configure(state="disabled")

    def action_load_data(self):
        """Paso 1: Carga los datos de los CSV a SQL."""
        self.status_label.configure(text=f"Cargando CSVs desde {CSV_FOLDER}...", text_color="gray")
        self.update_idletasks()
        
        success, message = load_all_csv_to_sql()
        
        if success:
            self.status_label.configure(text=message, text_color="blue")
        else:
            self.status_label.configure(text=f"❌ ERROR: {message}", text_color="red")

    def action_create_view(self):
        """Paso 2: Crea la vista unificada en SQL Server."""
        self.status_label.configure(text="Creando/Actualizando Vista SQL...", text_color="gray")
        self.update_idletasks()
        
        success, message = create_unified_view()
        
        if success:
            self.status_label.configure(text=message, text_color="blue")
        else:
            self.status_label.configure(text=f"❌ ERROR: {message}", text_color="red")

    def action_run_analysis(self):
        """Paso 3: Ejecuta la consulta de análisis de trayectoria."""
        self.status_label.configure(text="Ejecutando análisis de trayectoria...", text_color="gray")
        self.update_idletasks()

        df_result, message = get_repeated_mruns_analysis()
        
        if df_result is not None:
            output_file = "resultados_trayectoria_externa.xlsx"
            df_result.to_excel(output_file, index=False)
            
            final_msg = f"{message} Resultados detallados guardados en: '{output_file}'"
            self.status_label.configure(text=final_msg, text_color="darkgreen")
        else:
            self.status_label.configure(text=f"❌ ERROR: {message}", text_color="red")


if __name__ == "__main__":
    app = MatriculaApp()
    app.mainloop()