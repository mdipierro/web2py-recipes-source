# coding: utf8

class PluginWikiWidgets(PluginWikiWidgets):
    @staticmethod
    def aggregator(feed, max_entries=5):
        import gluon.contrib.feedparser as feedparser
        d = feedparser.parse(feed)
        title = d.channel.title
        link = d.channel.link
        description = d.channel.description
        div = DIV(A(B(title[0], _href=link[0])))
        created_on = request.now
        for entry in d.entries[0:max_entries]:
            div.append(A(entry.title,' - ', entry.updated, _href=entry.link))
            div.append(DIV(description))
        return div
        

"""
# Bogdan improvement

class PluginWikiWidgets(PluginWikiWidgets):
    @staticmethod
    def aggregator(feeds, max_entries=5):
        import gluon.contrib.feedparser as feedparser
        lfeeds = feeds.split(",")
        strg='''
            <script>
               var divDia = document.createElement("div");
               divDia.id ="dialog";
               document.body.appendChild(divDia);
               var jQuerydialog=jQuery("#dialog").dialog({
                           autoOpen: false,
                           draggable: false,
                           resizable: false,
                           width: 500
                         });
            </script>
            '''
        for feed in lfeeds:
            d = feedparser.parse(feed)
            title=d.channel.title,
            link = d.channel.link,
            description = d.channel.description
            created_on = request.now
            strg+='<a class="feed_title" href="%s">%s</a>' % (link[0],title[0])
            for entry in d.entries[0:max_entries]:
                strg+='''
                <div class="feed_entry">
                   <a rel="%(description)s" href="%(link)s">%(title)s - %(updated)s</a>
                   <script>
                      jQuery("a").mouseover(function () {
                           var msg = jQuery(this).attr("rel");
                           if (msg) {
                                jQuerydialog[0].innerHTML = msg;
                                jQuerydialog.dialog("open");
                                jQuery(".ui-dialog-titlebar").hide();
                            }
                      }).mousemove(function(event) {
                            jQuerydialog.dialog("option", "position", {
                                my: "left top",
                                at: "right bottom",
                                of: event,
                                offset: "10 10"
                            });
                      }).mouseout(function(){
                            jQuerydialog.dialog("close");
                      });
                  </script>
                </div>''' % entry
        return XML(strg)

"""
