import pandas as pd
import matplotlib.pyplot as plt
import glob

# Define the types and amounts
types = ['pqc', 'all', 'browser', 'os']
amounts = [1, 5, 10, 15, 20]

# Create a dictionary to hold data for each type
type_data = {t: {amount: [] for amount in amounts} for t in types}

# Load CSV files and organize data
for file in glob.glob("new-*-with-*-packets-results.csv"):
    type_part = file.split('-')[1]  # Extract type from the filename
    amount_part = int(file.split('-')[3])  # Extract amount from the filename

    # Load the CSV file
    df = pd.read_csv(file)

    # print(f'{df['Accuracy']=}\n{type(df['Accuracy'])=}')
    # print(f'{df['Accuracy'].str=}\n{type(df['Accuracy'].str)=}')
    # print(f'{df['Accuracy'].str.split(' +/- ', expand=True)=}\n{type(df['Accuracy'].str.split(' +/- ', expand=True))=}')

    # Extract accuracy data
    # accuracy_values = df['Accuracy'].str.split(' +/- ', expand=True)[0].astype(float).tolist()
    accuracy_values = [float(val.split(' +/- ')[0]) for val in df['Accuracy'].tolist()]
    print(accuracy_values)

    # Store the accuracy data for the specific type and amount
    type_data[type_part][amount_part] = accuracy_values


print(f'{type_data=}')


# Create separate plots for each type
for t in types:
    plt.figure(figsize=(20, 12))

    # Loop through each model and plot the data
    for model_index, model in enumerate(df['Model']):
        plt.plot(amounts, [type_data[t][amount][model_index] for amount in amounts], marker='o', label=model)

    # Customize the plot
    plt.title(f'Model Accuracy vs Amount of Packets - Type: {t}')
    plt.xlabel('Amount of Packets')
    plt.ylabel('Accuracy')
    plt.xticks(amounts)
    # plt.ylim(0, 1)  # Set y-axis limits for accuracy
    plt.legend(title='Models', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid()
    plt.tight_layout()

    # Show or save the plot
    plt.show()  # or
    # plt.savefig(f'accuracy_plot_{t}.png')

