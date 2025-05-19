class ConsoleUI:
    def __init__(self, mqtt_app):
        self.mqtt_app = mqtt_app

    def stop(self):
        pass

    def run_ui(self):
        def status():
            print("State")
            print(f"  Host:       {self.mqtt_app.config.mqtt.broker.host}")
            print(f"  Connection: {'online 🟢' if self.mqtt_app.mqtt_client.is_connected() else 'offline 🔴'}")


        def menu():
            title = self.mqtt_app.NAME.replace("-", " ").title()
            print(f"\n====== {title} {self.mqtt_app.VERSION} – Menu ==========================")
            status()
            print("=============================")
            print("1. Refresh state")
            print("2. Manual: Shutdown")
            print("3. Manual: Reboot")
            print("4. Restart app")
            print("q. Exit")
            print("============================")

        while self.mqtt_app.should_run:
            menu()
            choice = input("Eingabe: ").strip().lower()
            if choice == "1":
                status()
            elif choice == "2":
                self.mqtt_app.shutdown()
            elif choice == "3":
                self.mqtt_app.reboot()
            elif choice == "4":
                self.mqtt_app.restart()
            elif choice == "q":
                self.mqtt_app.exit_app()
            else:
                print("❓ Invalid input")
