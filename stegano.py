import os
import cv2
import numpy as np
import secrets

from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.filedialog import asksaveasfile


root = Tk()
root.geometry("500x500")
root.title("StenoPy v1.0")


# containment class
class CurrentImage:
   def __init__(self):
      self.image = None
      self.frame = None
      self.key = None
      self.message = None
      self.imageLocation = None
      self.messageLocation = None
      self.keyLocation = None


# converts string to bits
def ascii2bit(message):
   return ''.join(format(ord(char), '08b') for char in message)


# converts bits back to string
def bits2ascii(bits):
   bytes = [bits[i:i+8] for i in range(0, len(bits), 8)]
   return ''.join(chr(int(byte, 2)) for byte in bytes)


# generate message size
def genMessSize(bits):
   length = bin(len(bits))[2:]
   temp = ''
   for p in range(32 - len(length)):
      temp += '0'
   return temp + length + bits


# retrieve message size from header
def getMessSize(bits):
   return int(bits[:32], 2)


# encodes message into image
def encode(c):
   bits = genMessSize(ascii2bit(c.message))
   pos = 0
   flag = False
   h, w, _ = c.image.shape
   for y in range(h):
      for x in range(w):
         for k in range(2):
            r = c.image[y, x, k]
            r = bin(int(r))[2:]
            r = r[:-1] + bits[pos]
            c.image[y, x, k] = int(r, 2)
            pos += 1
            if pos == len(bits):
               flag = True
               break
         if flag == True:
            break
      if flag == True:
         break

   messagebox.showinfo(title="Status", message="Encoding Complete")
   clearFrame(c.frame)
   gui(c)


# decodes image data back into message
def decode(c, decrypt=0):
   bits = ''
   pos = 0
   h, w, _ = c.image.shape
   for y in range(h):
      for x in range(w):
         for k in range(2):
            r = c.image[y, x, k]
            r = bin(int(r))[2:]
            bits += r[-1]
            pos += 1
            if pos == 32:
               break
         if pos == 32:
            break
      if pos == 32:
         break
   
   size = getMessSize(bits) + 32
   bits = ''
   pos = 0
   for y in range(h):
      for x in range(w):
         for k in range(2):
            r = c.image[y, x, k]
            r = bin(int(r))[2:]
            bits += r[-1]
            pos += 1
            if pos == size:
               break
         if pos == size:
            break
      if pos == size:
         break

   bits = bits[32:]

   # if decrypting do not throw back to gui yet
   if decrypt == 1:
      return bits2ascii(bits)

   c.message = bits2ascii(bits)
   messagebox.showinfo(title="Message", message=c.message)
   clearFrame(c.frame)
   gui(c)


# encrypts message with key and encodes message to image
def encrypt(c):
   encrypted_message = ""
   for i, char in enumerate(c.message):
      encrypted_char = chr(ord(char) ^ ord(c.key[i % len(c.key)]))
      encrypted_message += encrypted_char
   c.message = encrypted_message
   return encode(c)


# decodes image and decrypts message with key
def decrypt(c):
   decrypted_message = ""
   encrypted_message = decode(c, 1)
   for i, char in enumerate(encrypted_message):
      decrypted_char = chr(ord(char) ^ ord(c.key[i % len(c.key)]))
      decrypted_message += decrypted_char
   c.message = decrypted_message
   messagebox.showinfo(title="Message", message=c.message)
   clearFrame(c.frame)
   gui(c)


# save image to file
def saveImage(image, file):
   path = file.name
   cv2.imwrite(path, image)
   messagebox.showinfo(title="Status", message="Saving Image Complete")


# generates image location text on gui
def genImageFound(c):
   if (c.image is not None):
      return os.path.basename(c.imageLocation)
   return "No Image Found."


# generates key location text on gui
def genKeyFound(c):
   if (c.key is not None):
      return os.path.basename(c.keyLocation)
   return "No Key Found."


# generates message location text on gui
def genMessageFound(c):
   if (c.message is not None and c.message is not type(str)):
      return os.path.basename(c.messageLocation)
   return "No Message Found."


# get file path with dialog
def getImageSavePath(c):
   file = asksaveasfile(mode='w', defaultextension=".png")
   if file is None:
      return
   c.imageLocation = file.name
   saveImage(c.image, file)
   clearFrame(c.frame)
   gui(c)


# load message to encode
def loadMessage(c):
   try:
      c.messageLocation = filedialog.askopenfilename()
      with open(c.messageLocation, 'r') as file:
         c.message = ''
         for line in file:
            c.message += line
         file.close()
   except Exception as e:
      c.message = None
   clearFrame(c.frame)
   gui(c)


# save message to text file
def saveMessage(c):
   file = asksaveasfile(mode='w', defaultextension=".txt")
   if file is None:
      return
   file.write(c.message)
   file.close()
   messagebox.showinfo(title="Status", message="Saving Message Complete")
   clearFrame(c.frame)
   gui(c)


# generate new key and prompt user if one already exists
def generateKey(c):
   c.key = secrets.token_hex(256)
   # make sure the user is ok with overwriting their current key
   c.keyLocation = "key.txt"
   ans = messagebox.askquestion(title="Key Generator", message="You are about to overwrite the contents of key.txt. If you do this, you will not be able to retrieve that key ever again. Are you sure you want to do this?")
   if ans == "no":
      return
   try:
      with open(c.keyLocation, 'w') as f:
         f.write(c.key)
         f.close()
   except Exception as e:
      print("Error writing key") # give dedicated message
      return None
   clearFrame(c.frame)
   gui(c)


# open file containing key and read key
def loadKey(c):
   try:
      c.keyLocation = filedialog.askopenfilename()
      with open(c.keyLocation, 'r') as f:
         c.key = f.read()
         f.close()
   except Exception as e:
      c.key = None
   clearFrame(c.frame)
   gui(c)
   

# choose image and generate image object
def chooseImage(c):
   c.imageLocation = filedialog.askopenfilename()
   c.image = cv2.imread(c.imageLocation)
   clearFrame(c.frame)
   gui(c)


# clear items in frame
def clearFrame(frame):
   frame.pack_forget()
   frame.destroy()


# build the frame 
def buildFrame(frame=None):
   if frame != None:
      return Frame(frame)
   else:
      return Frame(root)
   

# main gui
def gui(c):
   if c.frame != None:
      clearFrame(c.frame)
   frame = buildFrame()
   frame.pack()
   c.frame = frame

   headerText = Label(frame, text="SteganoPy", font=("IBM Plex Sans", 20))
   imageBtn = Button(frame, text="Load Image", bd="5", command=lambda: chooseImage(c))
   imageLabel = Label(frame, text=genImageFound(c), font=("IBM Plex Sans", 12))
   keyLabel = Label(frame, text=genKeyFound(c), font=("IBM Plex Sans", 12))
   messageLabel = Label(frame, text=genMessageFound(c), font=("IBM Plex Sans", 12))
   keyBtn = Button(frame, text="Load Key", bd="5", command=lambda: loadKey(c))
   generateBtn = Button(frame, text="Generate Key", bd="5", command=lambda: generateKey(c))
   saveImage = Button(frame, text="Save Image", bd="5", command=lambda: getImageSavePath(c))
   encodeImage = Button(frame, text="Encode Image", bd="5", command=lambda: encode(c))
   decodeImage = Button(frame, text="Decode Image", bd="5", command=lambda: decode(c))
   encryptImage = Button(frame, text="Encrypt Image", bd="5", command=lambda: encrypt(c))
   decryptImage = Button(frame, text="Decrypt Image", bd="5", command=lambda: decrypt(c))
   loadMess = Button(frame, text="Load Message", bd="5", command=lambda: loadMessage(c))
   saveMess = Button(frame, text="Save Message", bd="5", command=lambda: saveMessage(c))


   headerText.grid(row = 0, column = 0, pady=(15, 15))
   imageBtn.grid(row = 1, column = 0, pady=(15, 15))
   saveImage.grid(row = 1, column = 1, pady=(15, 15))
   imageLabel.grid(row = 1, column = 2, pady=(15, 15))
   keyBtn.grid(row = 2, column = 0, pady=(15, 15))
   generateBtn.grid(row = 2, column = 1, pady=(15, 15))
   keyLabel.grid(row = 2, column = 2, pady=(15, 15))
   loadMess.grid(row = 3, column = 0, pady=(15, 15))
   saveMess.grid(row = 3, column = 1, pady=(15, 15))
   messageLabel.grid(row = 3, column = 2, pady=(15, 15))
   encodeImage.grid(row = 4, column = 0, pady=(15, 15))
   decodeImage.grid(row = 4, column = 1, pady=(15, 15))
   encryptImage.grid(row = 5, column = 0, pady=(15, 15))
   decryptImage.grid(row = 5, column = 1, pady=(15, 15))

   return 1


# look, it's main
def main():
   gui(CurrentImage())
   root.mainloop()


if __name__=="__main__":
   main()
