import threading

class ConsoleUI:
    def __init__(self, appState):
        self.appState = appState
        self.thread = threading.Thread(target=self.runUI, daemon=True)

    def start(self):
        self.thread.start()

    def stop(self):
        pass

    def runUI(self):
        def status():
            print(f"State")  
            print(f"  Host:       {self.appState.config.mqtt.broker.host}")
            print(f"  Connection: {'online 🟢' if self.appState.mqttClient.is_connected() else 'offline 🔴'}")


        def menu():
            print("\n====== MQTT Presence – Menu ==========================")
            status()
            print("=============================")
            print("1. Refresh state")
            print("2. Manual: Shutdown")
            print("3. Manual: Reboot")
            print("4. Restart app")
            print("q. Exit")
            print("============================")

        while self.appState.should_run:
            menu()
            choice = input("Eingabe: ").strip().lower()
            if choice == "1":
                status()
            elif choice == "2":
                self.appState.shutdown()
            elif choice == "3":
                self.appState.reboot()
            elif choice == "4":
                self.appState.restart();
            elif choice == "q":
                self.appState.exitApp()
            else:
                print("❓ Invalid input")

