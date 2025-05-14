from mqtt_presence.utils import Tools

class ConsoleUI:
    def __init__(self, mqttAPP):
        self.mqttAPP = mqttAPP

    def stop(self):
        pass

    def runUI(self):
        def status():
            print(f"State")  
            print(f"  Host:       {self.mqttAPP.config.mqtt.broker.host}")
            print(f"  Connection: {'online 🟢' if self.mqttAPP.mqttClient.is_connected() else 'offline 🔴'}")


        def menu():
            print(f"\n====== {Tools.APP_NAME.replace("-", " ").title()} {self.mqttAPP.version} – Menu ==========================")
            status()
            print("=============================")
            print("1. Refresh state")
            print("2. Manual: Shutdown")
            print("3. Manual: Reboot")
            print("4. Restart app")
            print("q. Exit")
            print("============================")

        while self.mqttAPP.should_run:
            menu()
            choice = input("Eingabe: ").strip().lower()
            if choice == "1":
                status()
            elif choice == "2":
                self.mqttAPP.shutdown()
            elif choice == "3":
                self.mqttAPP.reboot()
            elif choice == "4":
                self.mqttAPP.restart();
            elif choice == "q":
                self.mqttAPP.exitApp()
            else:
                print("❓ Invalid input")

