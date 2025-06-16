import pandas as pd

# Load the hospital data

hospital_data = pd.read_csv("hospitals_cleaned_india.csv")

# Function to search hospitals
def search_hospital():
    print("\n--- Hospital Search ---")
    print("Search by:\n1. Hospital Name\n2. City")
    choice = input("Enter choice (1 or 2): ").strip()

    if choice == '1':
        name_query = input("Enter hospital name to search: ").strip().lower()
        results = hospital_data[hospital_data['Hospital Name'].str.lower().str.contains(name_query)]
    elif choice == '2':
        city_query = input("Enter city name to search: ").strip().lower()
        results = hospital_data[hospital_data['City'].str.lower().str.contains(city_query)]
    else:
        print("Invalid choice. Please enter 1 or 2.")
        return

    if results.empty:
        print("\nNo matching hospitals found.")
    else:
        print("\n--- Search Results ---")
        for index, row in results.iterrows():
            print(f"\nHospital Name: {row['Hospital Name']}")
            print(f"Address: {row['Address']}")
            print(f"City: {row['City']}")
            print(f"Phone: {row['Phone']}")
            print(f"Pincode: {row['Pincode']}")
            print(f"State: {row['State']}")

# Run the search
if __name__ == "__main__":
    while True:
        search_hospital()
        cont = input("\nDo you want to search again? (yes/no): ").strip().lower()
        if cont != 'yes':
            print("\nThank you for using Hospital Search!")
            break
