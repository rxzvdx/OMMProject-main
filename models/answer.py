# SWE Team 6:
# Joseph, Tyler, Antonio, Ross, Kashan, Gavin
# File:answer.py 
# Purpose: Manages each answer to the questions by setting the text, if the answer is correct, and the ID of the answer.
# Last edited: 02/06/2025

class Answer:    
    def __init__(self, answerID, answerText, isCorrect):
        self.answerText = answerText
        self.isCorrect = isCorrect
        self.answerID = answerID


    #setters
    def setAnswerText(self, answerText):
        self.answerText = answerText

    def setIsCorrect(self, isCorrect):
        self.isCorrect = isCorrect

    def setAnswerID(self, answerID):
        self.answerID = answerID

    #getters
    def getAnswerText(self):
        return self.answerText

    def getIsCorrect(self):
        return self.isCorrect

    def getAnswerID(self):
        return self.answerID
