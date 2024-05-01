import os
import cv2
import numpy as np
import time
import hashlib
import secrets

from tkinter import *
from tkinter import filedialog

root = Tk()
root.geometry("500x500")
root.title("StenoPy v1.0")

# converts string to bits
def ascii2bit(message):
   return ''.join(format(ord(char), '08b') for char in message)


# converts bits back to string
def bits2ascii(bits):
   bytes = [bits[i:i+8] for i in range(0, len(bits), 8)]
   return ''.join(chr(int(byte, 2)) for byte in bytes)


# encodes message into image
def encode(image, message):
   bits = ascii2bit(message)
   pos = 3
   h, w, _ = image.shape
   for y in range(h):
      for x in range(w):
         px = image[y, x]
         r = bin(px[0][2:0])
         g = bin(px[1][2:0])
         b = bin(px[2][2:0])

         r[-1] = bits[pos]
         g[-1] = bits[pos+1]
         b[-1] = bits[pos+2]

         px[0] = int(r, 2)
         px[1] = int(g, 2)
         px[2] = int(b, 2)

         image[y, x] = px
         pos += 3

   return image


# decodes image data back into message
def decode(image):
   bits = '08b'
   pos = 3
   h, w, _ = image.shape
   for y in range(h):
      for x in range(w):
         px = image[y, x]
         r = bin(px[0][2:0])
         g = bin(px[1][2:0])
         b = bin(px[2][2:0])

         bits[pos] = r[-1]
         bits[pos+1] = g[-1]
         bits[pos+2] = b[-1]
         pos += 3 

   return bits2ascii(bits)


# encrypts message with key and encodes message to image
def encrypt(image, message, key):
   encrypted_message = ""
   for char in message:
      encrypted_char = chr(ord(char) ^ key)
      encrypted_message += encrypted_char
   return encode(image, encrypted_message)


# decodes image and decrypts message with key
def decrypt(image, key):
   encrypted_message = decode(image)
   for char in encrypted_message:
      decrypted_char = chr(ord(char) ^ key)
      decrypted_message += decrypted_char
   return decrypted_message


# save image to file
def saveImage(image, path):
   cv2.imwrite(path, image)


# main gui
def gui(frame0=None, image=None, key=None):
   if frame0 != None:
      clearFrame(frame0)
   frame = buildFrame()
   frame.pack()

   headerText = Label(frame, text="StenoPy", font=("IBM Plex Sans",20))
   imageBtn = Button(frame, text="Image", bd="5", command=lambda: chooseImage(frame))
   keyBtn = Button(frame, text="Key", bd="5", command=lambda: loadKey(frame, image))
   generateBtn = Button(frame, text="Key", bd="5", command=lambda: generateKey(frame, image))
   


   return 1


# save text to file of user's choice
def saveText(text):
   f = loadFile("message.txt", 'w')
   if f != -1:
      f.write(text)
      return 0
   return -1


# generate new key and prompt user if one already exists
def generateKey(frame, image):
   key = secrets.token_hex(256)
   # make sure the user is ok with overwriting their current key
   f = loadFile("key.txt", 'w')
   if f != -1:
      f.write(key)
      f.close()
   else:
      print("Error writing key") # give dedicated message
   gui(frame, image, key)


# open file containing key and read key
def loadKey(frame, image):
   f = loadFile(filedialog.askopenfilename(), 'r')
   clearFrame(frame)
   if f != -1:
      key = f.read()
      f.close()
      return gui(frame, image, key)
   return gui(frame, image, -1)


# open file and return file object
def loadFile(filepath, mode):
   try:
      with open(filepath, mode) as f:
         return f
   except Exception as e:
      return -1
   

# choose image and generate image object
def chooseImage(frame):
   image = cv2.imread(filedialog.askopenfilename())
   clearFrame(frame)
   gui(frame, image)


# display a message to user
def displayMessage(frame):

   clearFrame(frame)
   gui(frame)


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


# command line alternative to gui
def cli():

   return 0


# look, it's main
def main():
   if args[0] != None:
      cli()
   root.mainloop()


if __name__=="__main__":
   main()
