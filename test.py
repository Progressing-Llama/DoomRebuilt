import tkinter as tk
from tkinter import messagebox
import json
from datetime import datetime
import os

# --- Configuration ---
DATA_FILE = "fuel_log.json"
INITIAL_PRICE_PER_LITER = 24.0
INITIAL_RATE_R_PER_KM = 1.9


class FuelTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("⛽ Fuel Cost Tracker (R/km)")
        master.geometry("600x550")
        master.configure(bg="#f0f0f0")

        # State Variables
        self.fuel_log = self.load_data()
        self.current_price_per_liter = self.fuel_log.get('price_per_liter', INITIAL_PRICE_PER_LITER)
        self.total_distance = self.fuel_log.get('total_distance', 0.0)

        # --- UI Setup ---
        self.setup_ui()
        self.update_display()

    def load_data(self):
        """Loads data from the JSON file."""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # If the file is corrupted or empty, return default structure
                return {"entries": [], "price_per_liter": INITIAL_PRICE_PER_LITER, "total_distance": 0.0}
        else:
            return {"entries": [], "price_per_liter": INITIAL_PRICE_PER_LITER, "total_distance": 0.0}

    def save_data(self):
        """Saves the current state to the JSON file."""
        self.fuel_log['price_per_liter'] = self.current_price_per_liter
        self.fuel_log['total_distance'] = self.total_distance
        with open(DATA_FILE, 'w') as f:
            json.dump(self.fuel_log, f, indent=4)

    def setup_ui(self):
        # --- Styling ---
        style = {
            "font": ("Arial", 12),
            "bg": "#f0f0f0",
            "padx": 10,
            "pady": 10,
            "relief": tk.SOLID
        }

        # --- Main Frame ---
        main_frame = tk.Frame(self.master, bg="#fff", padx=20, pady=20, borderwidth=2, relief=tk.GROOVE)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Price Control Section ---
        price_frame = tk.LabelFrame(main_frame, text="⚙️ Current Price Settings", padx=10, pady=10, bg="#e6f7ff")
        price_frame.pack(fill=tk.X, pady=10)

        tk.Label(price_frame, text="Price per Liter (R):", **style).grid(row=0, column=0, sticky="w", pady=5)
        self.price_entry = tk.Entry(price_frame, width=15, font=("Arial", 12), justify=tk.RIGHT)
        self.price_entry.insert(0, str(self.current_price_per_liter))
        self.price_entry.grid(row=0, column=1, sticky="e", padx=10)
        tk.Button(price_frame, text="Update Price", command=self.update_price, bg="#4CAF50", fg="white",
                  font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5)

        # --- Entry Section ---
        entry_frame = tk.LabelFrame(main_frame, text="⛽ Log Fuel Purchase", padx=10, pady=10, bg="#fff")
        entry_frame.pack(fill=tk.X, pady=10)

        tk.Label(entry_frame, text="Rand Spent (R):", **style).grid(row=0, column=0, sticky="w", pady=5)
        self.rand_entry = tk.Entry(entry_frame, width=15, font=("Arial", 12), justify=tk.RIGHT)
        self.rand_entry.grid(row=0, column=1, sticky="e", padx=10)

        tk.Label(entry_frame, text="Distance Driven (km):", **style).grid(row=1, column=0, sticky="w", pady=5)
        self.km_entry = tk.Entry(entry_frame, width=15, font=("Arial", 12), justify=tk.RIGHT)
        self.km_entry.grid(row=1, column=1, sticky="e", padx=10)

        tk.Button(entry_frame, text="Add Entry & Calculate Rate", command=self.add_entry, bg="#2196F3", fg="white",
                  font=("Arial", 10, "bold")).grid(row=2, column=0, columnspan=2, pady=15)

        # --- Display Section ---
        display_frame = tk.LabelFrame(main_frame, text="📊 Summary", padx=10, pady=10, bg="#e0f7fa")
        display_frame.pack(fill=tk.X, pady=10)

        self.lbl_total_km = tk.Label(display_frame, text=f"Total Distance: {self.total_distance:.2f} km",
                                     font=("Arial", 14, "bold"), bg="#e0f7fa")
        self.lbl_total_km.pack(pady=5)

        self.lbl_rate_info = tk.Label(display_frame, text="Current R/km: N/A", font=("Arial", 14, "bold"), bg="#e0f7fa")
        self.lbl_rate_info.pack(pady=5)

        # --- Log Display ---
        log_frame = tk.LabelFrame(main_frame, text="📜 History Log", padx=5, pady=5, bg="#fff")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.log_text = tk.Text(log_frame, height=15, width=50, font=("Consolas", 10), state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)

    def update_price(self):
        """Updates the price per liter and recalculates the display."""
        try:
            new_price = float(self.price_entry.get())
            if new_price <= 0:
                raise ValueError
            self.current_price_per_liter = new_price
            self.save_data()
            messagebox.showinfo("Success", f"Price updated to R{new_price:.2f}/L.")
            self.update_display()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number for the price.")

    def add_entry(self):
        """Handles adding a new fuel entry and calculating the rate."""
        try:
            rand_spent = float(self.rand_entry.get())
            distance = float(self.km_entry.get())

            if rand_spent <= 0 or distance <= 0:
                raise ValueError("Rand spent and distance must be positive values.")

            # Calculation: Rate (R/km) = (Total Rand Spent / Total Distance)
            rate = (rand_spent / distance)

            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "rand_spent": rand_spent,
                "distance_km": distance,
                "rate_r_per_km": rate
            }

            # Update state
            self.fuel_log['entries'].append(entry)
            self.total_distance += distance
            self.save_data()

            # Update UI
            self.log_entry(entry)
            self.update_display()

            # Clear fields
            self.rand_entry.delete(0, tk.END)
            self.km_entry.delete(0, tk.END)

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")

    def log_entry(self, entry):
        """Appends a new entry to the text log."""
        self.log_text.config(state=tk.NORMAL)

        log_line = (
            f"[{entry['timestamp']}] "
            f"Spent: R{entry['rand_spent']:8.2f} | "
            f"Distance: {entry['distance_km']:8.2f} km | "
            f"Rate: R{entry['rate_r_per_km']:8.3f} /km\n"
        )
        self.log_text.insert(tk.END, log_line)
        self.log_text.see(tk.END)  # Scroll to the bottom
        self.log_text.config(state=tk.DISABLED)

    def update_display(self):
        """Updates the overall summary labels."""
        self.lbl_total_km.config(text=f"Total Distance: {self.total_distance:.2f} km")

        # Display the rate of the *last* entry
        if self.fuel_log['entries']:
            last_entry = self.fuel_log['entries'][-1]
            rate_display = f"Current R/km (Last Entry): R{last_entry['rate_r_per_km']:.3f}"
        else:
            rate_display = "Current R/km: No entries yet."

        self.lbl_rate_info.config(text=rate_display)


if __name__ == "__main__":
    root = tk.Tk()
    app = FuelTrackerApp(root)
    root.mainloop()