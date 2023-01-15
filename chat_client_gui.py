import pickle
import socket
import threading
from tkinter import *
from tkinter import messagebox

# Window
window = Tk()
window.title("PyChat")
window.geometry("1366x768")

class Client:
    def __init__(self):
        self.SERVER = ""
        self.PORT = 5050
        self.ADDR = (self.SERVER, self.PORT)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Maximum 20 People (Name Length Limit will be 16 Characters)
        self.people = []

        # Only the latest 10 messages are shown at a time
        self.chatMsgs = []

        # Contains a Label which is a number showing total people connected to the server
        self.totalPeopleConnectedLabelList = []

        # Contains a Label which are names of all the people connected to the server
        self.numberOfPeopleConnectedLabelList = []

        # Contains a Label which are the 10 latest Messages in the server
        self.currentChatMsgsLabelList = []

    def connectClientToServer(self, serverIP):
        self.SERVER = serverIP
        self.ADDR = (self.SERVER, self.PORT)

        try:
            self.client.connect(self.ADDR)
            return 1
        except Exception as e:
            print(e)
            return -1

    def sendNameToServer(self, name):
        self.client.send(pickle.dumps(name))

    def sendMsgToServer(self, msg):
        self.client.send(pickle.dumps(msg))
        userMsgInput.delete("1.0", END)

    def getDataFromServer(self):
        while True:
            data = pickle.loads(self.client.recv(4096))

            if data == "Close Connection":
                break

            self.people = data[0]
            self.chatMsgs = data[1]

            self.deletePreviousLabels()

            self.displayCurrentMessages()
            self.displayNumberOfConnectedPeople()
            self.displayNamesofConnectedPeople()

    # Delete Previous Data
    def deletePreviousLabels(self):
        # Destroy labels of all messages
        for message in self.currentChatMsgsLabelList:
            message[0].after(1, message[0].destroy())
            message[1].after(1, message[1].destroy())

        # Delete all the labels from the messages list
        for i in range(len(self.currentChatMsgsLabelList)):
            self.currentChatMsgsLabelList.pop()

        # Destroy labels of all names
        for name in self.numberOfPeopleConnectedLabelList:
            name.after(1, name.destroy())

        # Delete all the labels from the names list
        for i in range(len(self.numberOfPeopleConnectedLabelList)):
            self.numberOfPeopleConnectedLabelList.pop()

        # Destroy the label for the total number of people
        if len(self.totalPeopleConnectedLabelList) == 1:
            self.totalPeopleConnectedLabelList[0].after(1, self.totalPeopleConnectedLabelList[0].destroy())

    # Display Messages
    def displayCurrentMessages(self):
        for person_msgs in self.chatMsgs:
            person = Label(chatFrame, text = f"{person_msgs[0]}", font = ("Calibri", 15), fg = "dark blue", bg = "white")

            if len(person_msgs[1]) >= 64:
                message = Label(chatFrame, text = f"{person_msgs[1][:63]}", font = ("leelawadee", 20), bg = "white")
            else:
                message = Label(chatFrame, text = f"{person_msgs[1]}", font = ("leelawadee", 20), bg = "white")

            self.currentChatMsgsLabelList.append([person, message])

        initialMsgYPos = 15
        for msg in self.currentChatMsgsLabelList:
            msg[0].place(x = 10, y = initialMsgYPos)
            msg[1].place(x = 10, y = initialMsgYPos + 18)
            initialMsgYPos += 62

    # Shows total number of people currently connected to the server
    def displayNumberOfConnectedPeople(self):
        totalPeopleConnectedLabel = Label(chatFrame, text = f"{len(self.people)}", font = ("Calibri", 20), fg = "green", bg = "white")

        if len(self.totalPeopleConnectedLabelList) == 1:
            self.totalPeopleConnectedLabelList[0] = totalPeopleConnectedLabel
        else:
            self.totalPeopleConnectedLabelList.append(totalPeopleConnectedLabel)

        self.totalPeopleConnectedLabelList[0].place(x = 1310, y = 10)
    # Show names of connected people
    def displayNamesofConnectedPeople(self):
        for names in self.people:
            clientName = Label(chatFrame, text = f"{names}", font = ("Arial", 20), bg = "white")
            self.numberOfPeopleConnectedLabelList.append(clientName)

        initialnamesYPos = 50
        for names in self.numberOfPeopleConnectedLabelList:
            names.place(x = 1100, y = initialnamesYPos)
            initialnamesYPos += 30

# Create Client Object
client = Client()

# Connect to Server Function
def connectToServer(ip):
    if nameInput.get() == "":
        messagebox.showinfo("Error", "Please enter your name")
    elif len(nameInput.get()) > 16:
        messagebox.showinfo("Error", "Entered name is too long. Please enter a shorter name")
    else:
        connectionCode = client.connectClientToServer(ip)

        if connectionCode == 1:
            messagebox.showinfo("Connection Success", "You are now connected to the Server.")
            showChatScreen()
            client.sendNameToServer(nameInput.get())
            getDataThread = threading.Thread(target = client.getDataFromServer)
            getDataThread.start()
        else:
            messagebox.showinfo("Unable to Connect", "Server limit reached/Server not Available")

def asktoExit():
    if messagebox.askyesno("Exit?", "Are you sure you want to exit?"):
        client.sendMsgToServer("Disconnect")
        window.destroy()

# Go to Chat Screen
def showChatScreen():
    homeFrame.pack_forget()
    chatFrame.pack(expand = True, fill = BOTH)

# Home Screen
homeFrame = Frame(window, background = "white")
homeFrame.pack(expand = True, fill = BOTH)

# Title
title = Label(homeFrame, text = "PyChat", font = ("Cambria", 55), bg = "white").place(x = 570, y = 30)

# Enter Name Text
enterNameLabel = Label(homeFrame, text = "Enter your name", font = ("Calibri", 25), bg = "white").place(x = 585, y = 260)

# Name Input Field
nameInput = Entry(homeFrame, font = ("Arial", 22), width = 20)
nameInput.place(x = 545, y = 310)

# Enter IP Label Text
enterIPLabel = Label(homeFrame, text = "Enter Server IP", font = ("Calibri", 25), bg = "white").place(x = 595, y = 390)

# Server IP Address Input Field
serverIPInput = Entry(homeFrame, font = ("Arial", 22), width = 20)
serverIPInput.place(x = 545, y = 440)

# Connect to Server Button
enterChatButton = Button(homeFrame, text = "Connect", font = ("Calibri", 30), command = lambda : connectToServer(serverIPInput.get()))
enterChatButton.place(x = 615, y = 560)

# Chat Screen
chatFrame = Frame(window, background = "white")

# Show names of the people currently connected to the server
peopleConnectedLabel = Label(chatFrame, text = "People Connected:", font = ("Calibri", 20), bg = "white").place(x = 1100, y = 10)

# User Message Input Box
userMsgInput = Text(chatFrame, font = ("Arial", 20), width = 70, height = 2)
userMsgInput.place(x = 0, y = 670)

# Send Message Button
sendMsgButton = Button(chatFrame, text = "Send", font = ("Calibri", 40), width = 4, bg = "green", command = lambda: client.sendMsgToServer(userMsgInput.get(1.0, END)))
sendMsgButton.place(x = 1060, y = 670)

# Clear Message Button
exitButton = Button(chatFrame, text = "Exit", font = ("Calibri", 40), width = 5, bg = "red", command = asktoExit)
exitButton.place(x = 1200, y = 670)

window.mainloop()
