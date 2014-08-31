
class TimeLineItem(object):
    """
    A wrapping class over a content to be displayed in the timeline
    
    TODO : it is not saved in database. In a future release, timeline items
    will be created at content creation time  
    """    
    def __init__(self, item, date, user, template):
        """
        
        @param item: an object to be displayed in the timeline (tweet, 
            image, comment, post, track ...)
        @param date: the datetime of the item
        @param user: original poster
        @param template:  
        """        
        self.item = item
        self.date = date
        self.user = user
        self.template = template           
