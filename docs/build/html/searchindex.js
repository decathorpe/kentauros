Search.setIndex({envversion:47,filenames:["index","kentauros","kentauros.actions","kentauros.bootstrap","kentauros.build","kentauros.config","kentauros.construct","kentauros.init","kentauros.package","kentauros.source","kentauros.upload","modules"],objects:{"":{kentauros:[1,0,0,"-"]},"kentauros.actions":{Action:[2,2,1,""],BuildAction:[2,2,1,""],ChainAction:[2,2,1,""],CleanAction:[2,2,1,""],ConfigAction:[2,2,1,""],ConstructAction:[2,2,1,""],CreateAction:[2,2,1,""],ExportAction:[2,2,1,""],GetAction:[2,2,1,""],PrepareAction:[2,2,1,""],RefreshAction:[2,2,1,""],StatusAction:[2,2,1,""],UpdateAction:[2,2,1,""],UploadAction:[2,2,1,""],VerifyAction:[2,2,1,""]},"kentauros.actions.Action":{execute:[2,5,1,""]},"kentauros.actions.BuildAction":{execute:[2,5,1,""]},"kentauros.actions.ChainAction":{execute:[2,5,1,""]},"kentauros.actions.CleanAction":{execute:[2,5,1,""]},"kentauros.actions.ConfigAction":{execute:[2,5,1,""]},"kentauros.actions.ConstructAction":{execute:[2,5,1,""]},"kentauros.actions.CreateAction":{execute:[2,5,1,""]},"kentauros.actions.ExportAction":{execute:[2,5,1,""]},"kentauros.actions.GetAction":{execute:[2,5,1,""]},"kentauros.actions.PrepareAction":{execute:[2,5,1,""]},"kentauros.actions.RefreshAction":{execute:[2,5,1,""]},"kentauros.actions.StatusAction":{execute:[2,5,1,""]},"kentauros.actions.UpdateAction":{execute:[2,5,1,""]},"kentauros.actions.UploadAction":{execute:[2,5,1,""]},"kentauros.actions.VerifyAction":{execute:[2,5,1,""]},"kentauros.bootstrap":{ktr_bootstrap:[3,3,1,""],ktr_create_dirs:[3,3,1,""]},"kentauros.build":{Builder:[4,2,1,""],MockBuilder:[4,2,1,""]},"kentauros.build.Builder":{"export":[4,5,1,""],build:[4,5,1,""]},"kentauros.build.MockBuilder":{build:[4,5,1,""]},"kentauros.config":{cli:[5,0,0,"-"],common:[5,0,0,"-"],envvar:[5,0,0,"-"],fallback:[5,0,0,"-"]},"kentauros.config.cli":{get_cli_config:[5,3,1,""]},"kentauros.config.common":{ConfigException:[5,4,1,""],KtrConf:[5,2,1,""]},"kentauros.config.common.KtrConf":{from_file:[5,5,1,""],succby:[5,5,1,""],validate:[5,5,1,""]},"kentauros.config.envvar":{get_env_config:[5,3,1,""]},"kentauros.config.fallback":{get_fallback_config:[5,3,1,""]},"kentauros.conntest":{is_connected:[1,3,1,""]},"kentauros.construct":{Constructor:[6,2,1,""],SrpmConstructor:[6,2,1,""],rpm_spec:[6,0,0,"-"]},"kentauros.construct.Constructor":{"export":[6,5,1,""],build:[6,5,1,""],clean:[6,5,1,""],init:[6,5,1,""],prepare:[6,5,1,""]},"kentauros.construct.SrpmConstructor":{"export":[6,5,1,""],build:[6,5,1,""],clean:[6,5,1,""],init:[6,5,1,""],prepare:[6,5,1,""]},"kentauros.construct.rpm_spec":{RPMSpecError:[6,4,1,""],bump_release:[6,3,1,""],if_release:[6,3,1,""],if_version:[6,3,1,""],spec_bump:[6,3,1,""],spec_preamble_bzr:[6,3,1,""],spec_preamble_git:[6,3,1,""],spec_preamble_url:[6,3,1,""],spec_release_read:[6,3,1,""],spec_version_bzr:[6,3,1,""],spec_version_git:[6,3,1,""],spec_version_read:[6,3,1,""],spec_version_url:[6,3,1,""]},"kentauros.definitions":{ActionType:[1,2,1,""],BuilderType:[1,2,1,""],ConstructorType:[1,2,1,""],KtrConfType:[1,2,1,""],SourceType:[1,2,1,""],UploaderType:[1,2,1,""]},"kentauros.definitions.ActionType":{BUILD:[1,1,1,""],CHAIN:[1,1,1,""],CLEAN:[1,1,1,""],CONFIG:[1,1,1,""],CONSTRUCT:[1,1,1,""],CREATE:[1,1,1,""],EXPORT:[1,1,1,""],GET:[1,1,1,""],PREPARE:[1,1,1,""],REFRESH:[1,1,1,""],STATUS:[1,1,1,""],UPDATE:[1,1,1,""],UPLOAD:[1,1,1,""],VERIFY:[1,1,1,""]},"kentauros.definitions.BuilderType":{MOCK:[1,1,1,""],NONE:[1,1,1,""]},"kentauros.definitions.ConstructorType":{NONE:[1,1,1,""],SRPM:[1,1,1,""]},"kentauros.definitions.KtrConfType":{CLI:[1,1,1,""],DEFAULT:[1,1,1,""],ENV:[1,1,1,""],FALLBACK:[1,1,1,""],PROJECT:[1,1,1,""],SYSTEM:[1,1,1,""],USER:[1,1,1,""]},"kentauros.definitions.SourceType":{BZR:[1,1,1,""],GIT:[1,1,1,""],LOCAL:[1,1,1,""],NONE:[1,1,1,""],URL:[1,1,1,""]},"kentauros.definitions.UploaderType":{COPR:[1,1,1,""],NONE:[1,1,1,""]},"kentauros.init":{cli:[7,0,0,"-"],env:[7,0,0,"-"]},"kentauros.init.cli":{CLIArgs:[7,2,1,""],get_parsed_cli:[7,3,1,""]},"kentauros.init.cli.CLIArgs":{parse_args:[7,5,1,""]},"kentauros.package":{Package:[8,2,1,""],PackageError:[8,4,1,""]},"kentauros.package.Package":{update_config:[8,5,1,""]},"kentauros.source":{bzr:[9,0,0,"-"],common:[9,0,0,"-"],git:[9,0,0,"-"],local:[9,0,0,"-"],url:[9,0,0,"-"]},"kentauros.source.bzr":{BzrSource:[9,2,1,""]},"kentauros.source.bzr.BzrSource":{"export":[9,5,1,""],formatver:[9,5,1,""],get:[9,5,1,""],rev:[9,5,1,""],update:[9,5,1,""]},"kentauros.source.common":{Source:[9,2,1,""]},"kentauros.source.common.Source":{"export":[9,5,1,""],clean:[9,5,1,""],formatver:[9,5,1,""],get:[9,5,1,""],prepare:[9,5,1,""],refresh:[9,5,1,""],update:[9,5,1,""]},"kentauros.source.git":{GitSource:[9,2,1,""]},"kentauros.source.git.GitSource":{"export":[9,5,1,""],date:[9,5,1,""],formatver:[9,5,1,""],get:[9,5,1,""],rev:[9,5,1,""],update:[9,5,1,""]},"kentauros.source.local":{LocalSource:[9,2,1,""]},"kentauros.source.local.LocalSource":{formatver:[9,5,1,""],get:[9,5,1,""]},"kentauros.source.url":{UrlSource:[9,2,1,""]},"kentauros.source.url.UrlSource":{get:[9,5,1,""]},"kentauros.upload":{CoprUploader:[10,2,1,""],Uploader:[10,2,1,""]},"kentauros.upload.CoprUploader":{upload:[10,5,1,""]},"kentauros.upload.Uploader":{upload:[10,5,1,""]},kentauros:{"package":[8,0,0,"-"],actions:[2,0,0,"-"],bootstrap:[3,0,0,"-"],build:[4,0,0,"-"],config:[5,0,0,"-"],conntest:[1,0,0,"-"],construct:[6,0,0,"-"],definitions:[1,0,0,"-"],init:[7,0,0,"-"],source:[9,0,0,"-"],upload:[10,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","attribute","Python attribute"],"2":["py","class","Python class"],"3":["py","function","Python function"],"4":["py","exception","Python exception"],"5":["py","method","Python method"]},objtypes:{"0":"py:module","1":"py:attribute","2":"py:class","3":"py:function","4":"py:exception","5":"py:method"},terms:{"abstract":2,"case":9,"class":[1,2,4,5,6,7,8,9,10],"default":[1,2,5,7,9],"enum":[1,2],"export":[1,2,4,6,9],"function":[1,4,5,6,7,10],"new":6,"return":[2,5,6,7,9],"switch":[3,5],"true":[2,9],abbrevi:9,about:[2,5,8,9],access:9,act:5,action:[],actiontyp:[1,2],activ:9,actual:3,add:2,after:[3,9],all:[1,2,5,9],alreadi:[2,5,9],alwai:2,anoth:5,anymor:9,arbitrari:1,argument:7,associ:9,attempt:2,attribut:5,atyp:2,automat:9,avail:[2,9],back:2,base:[1,2,4,5,6,7,8,9,10],basedir:5,been:[3,5,9],behind:1,belong:9,between:[2,9],bool:2,bootstrap:[],branch:9,build:[],buildact:2,builder:[1,2,4],buildertyp:1,built:[2,4,5,6],bump:[2,6],bump_releas:6,bumpspec:6,bzr:6,bzrsourc:9,can:[2,5],chain:[1,2],chainact:2,chang:2,check:[2,9],clean:[1,2,6,9],cleanact:2,cli:3,cli_arg:7,cli_pars:7,cliarg:7,clone:9,cloud:2,code:[2,9],command:[2,5,9],commit:9,common:[],conf:[2,8,9],confdir:[3,5,8],config:3,configact:2,configexcept:5,configpars:[2,8],configur:[1,2,3,5,8,9],conftyp:5,connect:[1,9],construct:[],constructact:2,constructor:[1,2,6],constructortyp:1,contain:[1,2,4,5,6,8,9,10],content:[],copi:[2,6,9],copr:[1,10],coprupload:10,correspond:2,correspondig:9,creat:[1,2,3,6],createact:2,current:[2,9],data:8,datadir:[1,3,5,9],date:9,datetim:9,defin:[1,2,6],definiton:1,delet:9,depend:9,describ:1,dest:9,destin:9,determin:[2,5,9],did:2,dir:2,directori:[2,5,6,9],displai:2,doe:9,doesn:2,don:2,done:2,download:9,dummi:2,dure:5,effect:2,either:9,empti:2,env:[3,5],environ:5,envvar:[],eror:5,errmsg:5,error:[6,8],etc:[2,9],evalu:3,even:2,eventu:5,everi:2,everyth:[2,3,9],everywher:1,except:[5,6,8],execut:2,exist:[2,9],explicitli:5,exportact:2,extend:5,fail:[2,9],fallback:[],fals:[2,6,9],far:5,file:[2,3,5,6,7,9],file_obj:6,filenam:9,filepath:5,follow:2,forc:2,format:[6,9],formatv:9,found:[5,6,9],from:[2,5,7,9],from_fil:5,further:2,gener:2,get:[1,2,9],get_cli_config:5,get_env_config:5,get_fallback_config:5,get_parsed_cli:7,getact:2,git:6,gitsourc:9,given:[2,5],gone:9,handl:9,hash:9,have:[3,9],helper:6,here:2,hold:[2,8,9],hopefulli:6,host:[1,9],if_releas:6,if_vers:6,includ:[5,8],increas:2,increment:2,index:0,inform:[2,5,8,9],init:6,initialis:[2,7],insid:2,instanc:[2,9],intellig:6,is_connect:1,item:5,keep:9,kei:2,kept:9,kind:1,ktr:[1,2,3],ktr_bootstrap:3,ktr_create_dir:3,ktrconf:5,ktrconftyp:1,last:[2,9],later:5,launchpad:9,like:[],line:[2,5,6],list:5,local:4,localsourc:9,locat:5,look:5,mai:5,master:9,mean:2,method:[2,4,5,6,7,8,9,10],might:9,mock:1,mockbuild:4,modul:[],moment:[2,8],move:6,name:[2,8,9],neccesari:9,neccessari:[2,9],need:[6,9],neither:9,net:9,nice:[6,9],non:5,none:[1,5,9],nor:9,normal:9,number:[2,9],object:[2,4,5,6,7,8,9,10],occur:5,onc:9,onli:[2,8,9],option:5,order:5,orig:9,origin:9,other:5,otherwis:2,out:8,overrid:[5,7,9],overridden:2,packagedir:2,packageerror:8,packdir:5,page:0,paramet:[2,9],pars:[5,7,8],parse_arg:7,parser:7,path:9,pend:2,pkgname:9,place:[2,5],point:[2,9],possibl:1,prepar:[1,2,4,6,7,9],preparatori:2,prepareact:2,process:[5,9],project:1,purpos:9,put:9,quasi:2,rais:5,reachabl:1,reaction:2,read:[5,7],real:2,refer:2,refresh:[1,2,9],refreshact:2,releas:[2,6],relreset:6,remot:9,remov:2,replac:5,repo:9,repodir:9,repositori:[2,9],request:9,requst:9,reset:2,respect:[2,9],result:5,rev:9,revis:9,rpm:[4,6],rpm_spec:[],rpmdev:6,rpmspecerror:6,run:[2,4,9],save:9,saved_rev:9,sdir:9,search:0,section:2,self:[5,9],server:[9,10],servic:2,set:[2,5,9],sever:2,shallow:9,should:[2,9],smartli:2,someth:9,sourc:[3,4,5,6,7,8],sourcetyp:1,spec:[5,6],spec_bump:6,spec_preamble_bzr:6,spec_preamble_git:6,spec_preamble_url:6,spec_release_read:6,spec_version_bzr:6,spec_version_git:6,spec_version_read:6,spec_version_url:6,specdir:[3,5],specif:[2,9],specifi:[2,3,9],src:[4,6],srpm:1,srpmconstructor:6,stage:2,statu:1,statusact:2,step:9,store:[2,9],str:[2,9],string:[6,9],structur:8,subclass:[2,9],substitut:9,succbi:5,succe:2,success:[2,9],successfulli:9,support:1,system:[1,9],taglin:6,tarbal:[2,5,9],templat:2,temporari:[2,6],termin:2,test:1,thei:2,them:7,thi:[2,5,8,9],through:2,time:9,type:[1,2,9],unsuccess:9,updat:[1,2,9],update_config:8,updateact:2,upload:[],uploadact:2,uploadertyp:1,upstream:9,url:6,urlsourc:9,usabl:5,user:1,usual:9,valid:5,valu:[2,5,6,7,8,9],variabl:[2,3,5],verifi:[1,2,5],verifyact:2,version:[2,6,9],via:6,wai:2,went:2,were:[2,9],wget:9,when:[2,9],where:9,which:[2,5,9],without:2,work:2,write:[2,8],written:2,yet:9,yield:5},titles:["Welcome to kentauros&#8217;s documentation!","kentauros package","kentauros.actions package","kentauros.bootstrap package","kentauros.build package","kentauros.config package","kentauros.construct package","kentauros.init package","kentauros.package package","kentauros.source package","kentauros.upload package","kentauros"],titleterms:{action:2,bootstrap:3,build:4,bzr:9,cli:[5,7],common:[5,9],config:5,conntest:1,construct:6,content:[1,2,3,4,5,6,7,8,9,10],definit:1,document:0,env:7,envvar:5,fallback:5,git:9,indic:0,init:7,kentauro:[0,1,2,3,4,5,6,7,8,9,10,11],local:9,modul:[1,2,3,4,5,6,7,8,9,10],packag:[1,2,3,4,5,6,7,8,9,10],rpm_spec:6,sourc:9,submodul:[1,5,6,7,9],subpackag:1,tabl:0,upload:10,url:9,welcom:0}})