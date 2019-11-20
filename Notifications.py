import pickle

NOTIFICATIONFILEPATH = 'static/bdnotifications.nico'


class Notifications:

    def __init__(self):
        try:
            with open(NOTIFICATIONFILEPATH, 'rb') as notificationfile:
                self.allnotifications = pickle.load(notificationfile)
                notificationfile.close()
        except:
            self.allnotifications = dict()

    def updateFile(self):
        serialdata = pickle.dumps(self.allnotifications)
        with open(NOTIFICATIONFILEPATH, 'wb') as notificationfile:
            notificationfile.write(serialdata)
            notificationfile.close()

    def addUsers(self, userIds):
        for user in userIds:
            self.allnotifications[user['id']] = []

    def addUser(self, userId):
        if not self.__checkUserInDict(userId):
            self.allnotifications[userId] = []
            self.updateFile()
        else:
            raise Exception('User cannot be added to de dict')

    def addNotificationToList(self, userIdParam, info):
        for userId, notificationList in self.allnotifications.items():
            if userIdParam != userId:
                notificationListParam = notificationList
                notificationListParam.append(info)
                self.allnotifications[userId] = notificationListParam
        self.updateFile()

    def getInformationListForUser(self, userId):
        if userId in self.allnotifications:
            return self.allnotifications[userId]
        else:
            return None

    def deleteNotificationFromUserList(self, notificationIdParam, userId):
        if type(notificationIdParam) == str:
            for i in range(len(self.allnotifications[userId])):
                notificationId = self.allnotifications[userId][i]['notificationId']
                if notificationId == notificationIdParam:
                    del self.allnotifications[userId][i]
                    break
            self.updateFile()
        else:
            raise Exception("NotificationId must be string")

    def checkIfEmpty(self, userId):
        if self.allnotifications[userId]:
            return False
        else:
            return True

    def __checkUserInDict(self, userId):
        if userId in self.allnotifications:
            return True
        else:
            return False
