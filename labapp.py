import sys
import os

try:
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError:
    print("❌ Error: Missing required data libraries (pandas/matplotlib).")
    input("\nPress Enter to exit...")
    sys.exit()

# -------------------------------------------------------------
# TOOL 1: JAR TEST CALCULATOR
# -------------------------------------------------------------
def run_jar_test():
    print("\n" + "="*50)
    print("🧪 MODULE 1: COAGULATION JAR-TEST OPTIMIZATION")
    print("="*50)
    try:
        num_jars = int(input("Enter number of beakers tested: "))
    except ValueError:
        print("❌ Invalid number.")
        return

    lab_data = []
    for i in range(num_jars):
        jar_id = f"B{i+1}"
        print(f"\n--- Beaker {jar_id} ---")
        try:
            dose = float(input(f"  Imposed Dose (mg/L): "))
            turbidity = float(input(f"  Residual Turbidity (NTU): "))
            perf = input(f"  Floc Performance Notes: ").strip()
        except ValueError:
            print("❌ Invalid input. Skipping beaker.")
            continue
        lab_data.append({'Jar_ID': jar_id, 'Dose': dose, 'Turbidity': turbidity, 'Notes': perf if perf else "N/A"})

    df = pd.DataFrame(lab_data)
    optimum = df.loc[df['Turbidity'].idxmin()]

    print("\n📈 GENERATED REPORT:")
    print(df.to_string(index=False))
    print(f"\n🎯 OPTIMUM DOSE: {optimum['Dose']} mg/L (Residual Turbidity: {optimum['Turbidity']} NTU)")

    # Plotting Curve
    plt.figure(figsize=(7, 4))
    plt.plot(df['Dose'], df['Turbidity'], marker='o', color='#1f77b4', linewidth=2)
    plt.title('Jar Test Curve')
    plt.xlabel('Dose (mg/L)')
    plt.ylabel('Turbidity (NTU)')
    plt.grid(True, linestyle=':')
    plt.savefig('jar_test_output.png', dpi=300)
    print("💾 Curve plot saved as 'jar_test_output.png'")
    plt.close()

# -------------------------------------------------------------
# TOOL 2: BREAKPOINT CHLORINATION
# -------------------------------------------------------------
def run_breakpoint_chlorination():
    print("\n" + "="*50)
    print("🧪 MODULE 2: BREAKPOINT CHLORINATION CURVE")
    print("="*50)
    print("[Placeholder: Future chemistry calculations will process here!]")
    # We will build out this mathematical model in the next step!

# -------------------------------------------------------------
# MASTER DASHBOARD MENU
# -------------------------------------------------------------
def main_menu():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("="*65)
        print("   💧 ENVIRONMENTAL ENGINEERING: WATER TREATMENT LAB SUITE v1.0 💧   ")
        print("="*65)
        print(" [1] Coagulation & Flocculation (Jar Test)")
        print(" [2] Disinfection (Breakpoint Chlorination)")
        print(" [3] Gravimetric Analytics (Suspended Solids & TSS)")
        print(" [4] Groundwater Deferrization (Iron & Manganese)")
        print(" [5] Nitrate Adsorption Kinetics")
        print(" [6] Chemical Precipitation Softening (Lime-Soda)")
        print(" [0] Exit Application")
        print("="*65)
        
        choice = input("\n👉 Select a laboratory module to launch (0-6): ").strip()
        
        if choice == '1':
            run_jar_test()
            input("\nPress Enter to return to main menu...")
        elif choice == '2':
            run_breakpoint_chlorination()
            input("\nPress Enter to return to main menu...")
        elif choice in ['3', '4', '5', '6']:
            print("\n🚧 Module under active development in your Master's curriculum!")
            input("\nPress Enter to return to main menu...")
        elif choice == '0':
            print("\n👋 Closing suite. Happy analyzing!")
            break
        else:
            input("\n❌ Invalid choice. Press Enter to try again...")

if __name__ == "__main__":
    main_menu()
