from util.mysql_access.posts import DBPosts
from util.config import SO_POSTS_STORE_PATH

import pickle
import os

'''
EUREKA：非泛用式NER基础设施（目前）
生成的post schema
{
        "Id": 32913709,
        "Body": "<p>When the Gang of four introduced the singleton pattern, they also had to explain, why not to use static class fields and method instead. The reason was: the possibility to inherit. For Java it had sense - we cannot normally inherit the class fields and methods.</p>&#xA;&#xA;<p>Later the \"Effective Java\" book appeared. And we know now that the existence of reflection destroys the singularity of the singleton class with private constructor. And the only way to make a real SINGLEton is to make it as a single item of an enumeration. Nice. I had done some myself this way.</p>&#xA;&#xA;<p>But a question remains: While we cannot inherit from enumeration, what is the use of this singleton? Why we don't use these old good static/class fields and methods? </p>&#xA;&#xA;<p>Edit. Thanks to the @bayou.io I see that in <a href=\"https://softwareengineering.stackexchange.com/a/204181/44104\">https://softwareengineering.stackexchange.com/a/204181/44104</a> there is a code that can trick the enum, too, and create again two exemplars of the enum singleton. The other problems are mentioned there, too. So, there is no need to use enum instead of the usual singleton class pattern, too? BTW, all enum pluses that are mentioned here till now, work for singleton classes, too. </p>&#xA;",
        "Tags": "<java><design-patterns><singleton>",
        "Title": "What is the use of the enum singleton in Java?",
        "Score": 7,
        "ViewCount": 782,
        "FavoriteCount": 2,
        "Answers": [
            {
                "Body": "<p>There's nothing particularly wrong with the \"good old fashioned singleton\", enum \"singletons\" are just convenient - it saves you the need to muck around with boiler-plated code that looks the same in every singelton.</p>&#xA;",
                "Score": 2,
                "Accepted": false
            },
            {
                "Body": "<p>To me, a singleton makes sense wherever you want to represent something which is unique in its kind. </p>&#xA;&#xA;<p>As an example, if we wanted to model <em>the</em> <code>Sun</code>, it could not be a normal class, because there is only one <code>Sun</code>. However it makes sense to make it inherit from a <code>Star</code> class. In this case I would opt for a static instance, with a static getter.</p>&#xA;&#xA;<p>To clarify, here is what I'm talking about :</p>&#xA;&#xA;<pre><code>public class Star {&#xA;    private final String name;&#xA;    private final double density, massInKg;  &#xA;&#xA;    public Star(String name, double density, double massInKg) {&#xA;        // ...&#xA;    }&#xA;&#xA;    public void explode() {&#xA;       // ...&#xA;    }&#xA;}&#xA;&#xA;public final class Sun extends Star {&#xA;    public static final Sun INSTANCE = new Sun();&#xA;&#xA;    private Sun() { super(\"The shiniest of all\", /**...**/, /**...**/); }&#xA;}&#xA;</code></pre>&#xA;&#xA;<p><code>Sun</code> can use all the methods of <code>Star</code> and define new ones. This would not be possible with an enum (extending a class, I mean).</p>&#xA;&#xA;<p>If there is no need to model this kind of inheritance relationships, as you said, the <code>enum</code> becomes better suited, or at least easier and clearer. For example, if an application has a single <code>ApplicationContext</code> per JVM, it makes sense to have it as a singleton and it usually doesn't require to inherit from anything or to be extendable. I would then use an <code>enum</code>.</p>&#xA;&#xA;<p>Note that in some languages such as Scala, there is a special keyword for singletons (<code>object</code>) which not only enables to easily define singletons but also completely replaces the notion of static method or field.</p>&#xA;",
                "Score": 1,
                "Accepted": false
            },
            {
                "Body": "<p><strong>what is the use of this singleton? Why we don't use these old good static/class fields and methods?</strong></p>&#xA;&#xA;<p>Because <code>enum</code> is an object so it can not only be passed around but also implement interfaces.</p>&#xA;&#xA;<p>Also since we are making a class, we can use the different public/private options available to all kinds of classes.</p>&#xA;&#xA;<p>So in practice, we can make a singleton that implements an interface and then pass it around in our code and the calling code is non the wiser.  We can also make the enum class package private but still pass it around to other classes in other packages that expect the interface.</p>&#xA;&#xA;<p>If we used the static methods version, then the calling class would have to know that this object is a singleton, and our singleton class would have to be public so the other classes can see it and use it's methods.</p>&#xA;",
                "Score": 3,
                "Accepted": true
            },
            {
                "Body": "<ol>&#xA;<li><p><strong><em><code>ENUM</code></em></strong> singletons are easy to write. It will occupy very less code, which is clean  &amp; elegant if you compare with implementation of lazy singleton with double synchronized blocks  </p>&#xA;&#xA;<pre><code> public enum EasySingleton{&#xA;    INSTANCE;&#xA;}&#xA;</code></pre></li>&#xA;<li><p>Creation of <strong><em><code>ENUM</code></em></strong> instance is thread safe. </p></li>&#xA;<li><p><strong><em><code>ENUM</code></em></strong> singletons handled serialization by themselves.</p>&#xA;&#xA;<p>conventional Singletons  implementing <code>Serializable</code> interface are no longer remain Singleton because <code>readObject()</code> method always return a new instance just like constructor in Java. you can avoid that by using <code>readResolve()</code> method and discarding newly created instance by replacing with Singeton</p>&#xA;&#xA;<pre><code>private Object readResolve(){&#xA;    return INSTANCE;&#xA;}&#xA;</code></pre></li>&#xA;</ol>&#xA;&#xA;<p>Have a look at this <a href=\"http://javarevisited.blogspot.in/2012/07/why-enum-singleton-are-better-in-java.html\" rel=\"nofollow\">article on singleton</a></p>&#xA;",
                "Score": 0,
                "Accepted": false
            }
        ],
        "Links": [
            "https://softwareengineering.stackexchange.com/a/204181/44104",
            "http://javarevisited.blogspot.in/2012/07/why-enum-singleton-are-better-in-java.html"
        ]
    }
'''

def collect_so_posts_related_to(tag_name):
    '''
    ## collect all so posts that related to a tag
    the tag may mostly be a language, but there may be some other usage
    ### parameter: `tag_name`:
        the tag's name, which is a 'tag' such as '<java>' not just 'java'
    '''
    posts_db = DBPosts()
    cnt = 0
    so_posts_to_store = []
    for item in posts_db.collect_posts_by_tag(tag_name):
        so_posts_to_store.append(item)
        if len(so_posts_to_store) >= 50000:
            file_name = f"posts_{cnt}.pkl"
            file_store_path = os.path.join(SO_POSTS_STORE_PATH[tag_name], file_name)
            with open(file_store_path, 'wb') as wbf:
                pickle.dump(so_posts_to_store, wbf)
            del so_posts_to_store
            so_posts_to_store = []
            cnt += 1
            print("\r",f"{cnt * 50000} posts stored",end="",flush=True)
    if len(so_posts_to_store) > 0:
        file_name = f"posts_{cnt}.pkl"
        file_store_path = os.path.join(SO_POSTS_STORE_PATH[tag_name], file_name)
        with open(file_store_path, 'wb') as wbf:
            pickle.dump(so_posts_to_store, wbf)
        del so_posts_to_store
        cnt += 1
    print("\r","done!",end="",flush=True)


if __name__ == "__main__":
    collect_so_posts_related_to('<java>')

    