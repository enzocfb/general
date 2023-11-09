import pandas as pd
import os
from openpyxl import Workbook
import numpy as np

# for graphics
from matplotlib import pyplot as plt


def delete_columns_redundant(df, name_indicator, factor_redundant):
 
    df = df.drop(name_indicator, axis=1)
    df = df.drop(factor_redundant, axis=1)
    return df


# Añadimos el resultado del sub reporte por pais, al df acumulador

def increment_new_result_into_df(df, df_new, df_key_groupby, suffix1, suffix2):
    
    df = pd.merge(df, df_new, on = df_key_groupby, how='left',suffixes=(suffix1, suffix2))
    return df


# ----------------------------------------------

# Add fields metadata for identifying report

def insert_metadata(df,id_indicator, name_country):
    df.insert(0,'id_indicator', id_indicator)
    df.insert(1,'name_country', name_country)
    return df

def save_df_to_excel(df,file_output, boolean_with_index):
        
    df.index = df.index + 1
    
    if isinstance(boolean_with_index, bool):
        df.to_excel(file_output, index = boolean_with_index, startrow = 1, index_label = "id" )
    else:
        print("The value is not a boolean.")
    return 0

#df1.dropna(subset=['transit_to_superior']).to_excel(file_output, index_label = "id")

# Reindexing the DataFrame from 1 to n

def delete_rows_dataset_just_for_indicator(df, name_indicator):

    if type(name_indicator) == str:
        df = df.dropna(subset=[name_indicator])  
    elif type(name_indicator) == list:
        df = df.dropna(subset= name_indicator, how='all')

    # if isinstance(name_indicator, str):
    #     df.dropna(subset=[name_indicator], inplace=True)
    # elif isinstance(name_indicator, list):
    #     df.dropna(subset=name_indicator, how='all', inplace=True)

    print('Info del df: nro de filas: ',df.shape[0])
    return df

# Falta implementar
# def filter_just_indicador(df, name_indicator_list):  eliminar las filas nulas
# def read_csv_optimizer : optimizar memoria al leer csv grandes
# def calculate_sample_error (Calculo de error muestral)

# Function to round numeric columns to 2 decimal places
def round_numeric_columns(df):

    numeric_columns = df.select_dtypes(include=['float', 'int']).columns
  
    # Check if there are any numeric columns
    #if not numeric_columns.empty:
        # Round the numeric columns to two decimal places
    df[numeric_columns] = df[numeric_columns].round(2)

    return df

def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)

def optimize_numeric_dtypes(df, default_value):
    
    numeric_columns = df.select_dtypes(include=['int', 'float']).columns
    print('numeric_columns =', numeric_columns)

    for column in numeric_columns:
        #print('column =', column, 'tipo dato = ', df[column].dtypes, 'shape = ',  df[column].shape)
        df[column] = pd.to_numeric(df[column], errors='coerce', downcast='integer')
        #print('Termino = pd.to_numeric(df[column]', column)
        df[column] = np.where(pd.isnull(df[column]), default_value, df[column])
        #print('Termino = np.where(pd.isnull(df[column])', column)

    # Check if any values were converted to integer
    int_columns = df.select_dtypes(include=['integer']).columns
    float_columns = df.select_dtypes(include=['float']).columns

    # Convert remaining float columns to smaller float types
    df[float_columns] = df[float_columns].apply(pd.to_numeric, downcast='float')

    return df

class FileBase:

    def __init__(self, file_path):
        self.file_path = file_path      # nombre de archivo, con el cual se trabaja (excel or csv)

    def save_dataframe(self, df, overwrite):
        if os.path.exists(self.file_path) and not(overwrite):
            # File exists, append the DataFrame
            existing_data = pd.read_excel(self.file_path)
            updated_data = pd.concat([existing_data, df], ignore_index=True)
            updated_data.to_excel(self.file_path, index=False)
            print("DataFrame appended to the existing Excel file.")
        else:
            # File does not exist, create a new Excel file
            df.to_excel(self.file_path, index=False)
            print("DataFrame saved to a new Excel file.")

    def save_excel(self, sheet_name, index, title=None):
        writer = pd.ExcelWriter(self.file_path, engine='xlsxwriter')
        self.df.to_excel(writer, sheet_name=sheet_name, index=index,  index_label = "id", header=True)
        writer.save()
        print(f"DataFrame saved as {self.file_path} in sheet '{sheet_name}'")


    def evaluate_file_type_si_es_excel_or_csv(self, file_path):

        try:
            # Attempt to read the file as an Excel file
            excel_df = pd.read_excel(file_path)
            return "Excel"
        
        except Exception:
            try:
                # Attempt to read the file as a CSV file
                csv_df = pd.read_csv(file_path)
                return "CSV"
            
            except Exception:
                return "Unsupported"

    #     # Example usage:
    # file_path = "example.xlsx"  # Replace with the path to your file
    # evaluator = FileBase(file_path)
    # file_type = FileBase.evaluate_file_type_si_es_excel_or_csv(file_path)
    # print(f"The file type is: {file_type}")


    def delete_file(self):

        try:
            os.remove(self.filename)
            print("File deleted successfully.")
        except OSError as e:
            print(f"Error deleting the file: {e}")

    
    def split_df_into_sheets(self, df, list_sheets, list_dataframes):

        # Asumption
        # df has also columns that exists in list_sheets
        # ***************
        # example : how works
        # file_o.split_df_into_sheets(df, name_indicator, list_dataframes=[])

        list_length = len(list_sheets)
        excel_writer = pd.ExcelWriter(self.file_path, engine='xlsxwriter')

        print(list_sheets)
        
        if list_length > 1:

            for sheet_name  in list_sheets:
                df_temp = df
                # Creo el df especifico , por ejemplo si elijo un label, debo eliminar todos los otros labels, aunque manteniendo todos otros los campos del df
                print('sheet actual = ', sheet_name)
                my_list_to_eliminate = list_sheets.copy()
                my_list_to_eliminate.remove(sheet_name)   
                print('my_list_to_eliminate = ', my_list_to_eliminate)  

                #temp
                print(df_temp['id_nivel'].value_counts())
                df_splited = df_temp.drop(columns = my_list_to_eliminate)

                print('Nro, filas, columnas = ', df_splited.shape)  

                #df = df.dropna(subset=new_fields_list, how = 'all')
                
                df_splited = df_splited.dropna(subset=sheet_name)


                #self.file_path.add_sheet(sheet, df_splited)
                #df_splited.to_excel(excel_writer, sheet_name=sheet_name, index=True)
                df_splited.to_excel(excel_writer, sheet_name=sheet_name, index=True)
                

        else:
                sheet_name = list_sheets[0]
                new_df = self.df.dropna(subset=sheet_name)
                new_df.to_excel(excel_writer, sheet_name=sheet_name, index=True)
                
        i=0

        if len(list_dataframes) > 0:

            for df_add in list_dataframes:
                i = i+1
                sheet_name = str(i)
                df_add.to_excel(excel_writer, sheet_name=sheet_name, index=True)
        
        excel_writer.save()

    
    def dataframe_from_many_columns_to_one_column(df, list_columns, new_name_column, new_value_column):

    
        list_columns_df = df.columns.tolist()
        contador = 0

        for col in list_columns:
            contador += 1
            # Create a new list without the elements_to_remove
            new_list = [x for x in list_columns_df if x not in list_columns]

            #Le adicionamos la unica columna que quedara
            new_list.append(col)

            # 'new_list' will be the original list without the elements_to_remove
            
            df_new = df[new_list]
            df_new = df_new.rename(columns = {col: new_value_column})
            df_new[new_name_column] = col

            print('col =', col, 'lista nueva = ', new_list, 'nro de registros =', df_new.shape[0])
            
            if contador == 1:
                df_acum = df_new
            else:
                df_acum = pd.concat([df_acum, df_new])

        #df_acum.reindex
        print('numero de filas', contador)    

        return df_acum   

        """_summary_

        import pandas as pd

            data = {
                'Category': ['A', 'B', 'A', 'B', 'A', 'B'],
                'Value1': [10, 20, 15, 25, 30, 35],
                'Value2': [5, 15, 10, 20, 25, 30]
            }

        df = pd.DataFrame(data)
                print('df = \n', df)
                dataframe_from_many_columns_to_one_column(df, ['Value1', 'Value2'],'servicio')
        """

    # Create a function that we can re-use
    def show_distribution(col):
  
        # Get statistics
        min_val = col.min()
        max_val = col.max()
        mean_val = col.mean()
        med_val = col.median()
        mod_val = col.mode()[0]

        print('Minimum:{:.2f}\nMean:{:.2f}\nMedian:{:.2f}\nMode:{:.2f}\nMaximum:{:.2f}\n'.format(min_val,
                                                                                                mean_val,
                                                                                                med_val,
                                                                                                mod_val,
                                                                                                max_val))

        # Create a figure for 2 subplots (2 rows, 1 column)
        fig, ax = plt.subplots(2, 1, figsize = (10,4))

        # Plot the histogram   
        ax[0].hist(col)
        ax[0].set_ylabel('Frequency')

        # Add lines for the mean, median, and mode
        ax[0].axvline(x=min_val, color = 'gray', linestyle='dashed', linewidth = 2)
        ax[0].axvline(x=mean_val, color = 'cyan', linestyle='dashed', linewidth = 2)
        ax[0].axvline(x=med_val, color = 'red', linestyle='dashed', linewidth = 2)
        ax[0].axvline(x=mod_val, color = 'yellow', linestyle='dashed', linewidth = 2)
        ax[0].axvline(x=max_val, color = 'gray', linestyle='dashed', linewidth = 2)

        # Plot the boxplot   
        ax[1].boxplot(col, vert=False)
        ax[1].set_xlabel('Value')

        # Add a title to the Figure
        fig.suptitle('Data Distribution')

        # Show the figure
        fig.show()

    # =========================
    # How to use
    # =========================
    # Select the column that you would like to analyze, example
    # col = df_students['Grade']

    # # After you Call the function, to analyze, minimum, mean, median, mode, and maximum in a graph, ploted and with their values
    # show_distribution(col)

    def show_density(col):
    

        fig = plt.figure(figsize=(10,4))

        # Plot density
        col.plot.density()

        # Add titles and labels
        plt.title('Data Density')

        # Show the mean, median, and mode
        plt.axvline(x=col.mean(), color = 'cyan', linestyle='dashed', linewidth = 2)
        plt.axvline(x=col.median(), color = 'red', linestyle='dashed', linewidth = 2)
        plt.axvline(x=col.mode()[0], color = 'yellow', linestyle='dashed', linewidth = 2)

        # Show the figure
        plt.show()

    # =========================
    # How to use
    # =========================
    # Select the column that you would like to analyze, example
    # # Get the density of Grade
    # col = df_students['Grade']
    # show_density(col)