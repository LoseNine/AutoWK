class Options:
    def __init__(
        self,
        x=0,
        y=0,
        width=0,
        height=0,
        lang="en-US",
        timezone="America/Chicago",
        proxyType=None,
        proxyHost=None,
        proxyPort=None,
        proxyUsername='',
        proxyPassword='',
        userDataDir='',
        fpfile='',
        userAgent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/605.1.15 (KHTML, like Gecko)',
        headless=False,
        enableListen=False,
        networkListenPort =0,
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.lang = lang
        self.timezone = timezone
        self.proxyType = proxyType
        self.proxyHost = proxyHost
        self.proxyPort = proxyPort
        self.proxyUsername = proxyUsername
        self.proxyPassword = proxyPassword
        self.userDataDir = userDataDir
        self.fpfile = fpfile
        self.userAgent = userAgent
        self.headless = headless
        self.enableListen=enableListen
        self.networkListenPort = networkListenPort
