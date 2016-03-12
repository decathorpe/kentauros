Search.setIndex({envversion:47,filenames:["apidoc/kentauros","apidoc/kentauros.actions","apidoc/kentauros.bootstrap","apidoc/kentauros.build","apidoc/kentauros.config","apidoc/kentauros.construct","apidoc/kentauros.init","apidoc/kentauros.package","apidoc/kentauros.source","apidoc/kentauros.upload","apidoc/modules","index"],objects:{"":{kentauros:[0,0,0,"-"]},"kentauros.actions":{Action:[1,2,1,""],BuildAction:[1,2,1,""],ChainAction:[1,2,1,""],CleanAction:[1,2,1,""],ConfigAction:[1,2,1,""],ConstructAction:[1,2,1,""],CreateAction:[1,2,1,""],ExportAction:[1,2,1,""],GetAction:[1,2,1,""],PrepareAction:[1,2,1,""],RefreshAction:[1,2,1,""],StatusAction:[1,2,1,""],UpdateAction:[1,2,1,""],UploadAction:[1,2,1,""],VerifyAction:[1,2,1,""]},"kentauros.actions.Action":{execute:[1,3,1,""]},"kentauros.actions.BuildAction":{execute:[1,3,1,""]},"kentauros.actions.ChainAction":{execute:[1,3,1,""]},"kentauros.actions.CleanAction":{execute:[1,3,1,""]},"kentauros.actions.ConfigAction":{execute:[1,3,1,""]},"kentauros.actions.ConstructAction":{execute:[1,3,1,""]},"kentauros.actions.CreateAction":{execute:[1,3,1,""]},"kentauros.actions.ExportAction":{execute:[1,3,1,""]},"kentauros.actions.GetAction":{execute:[1,3,1,""]},"kentauros.actions.PrepareAction":{execute:[1,3,1,""]},"kentauros.actions.RefreshAction":{execute:[1,3,1,""]},"kentauros.actions.StatusAction":{execute:[1,3,1,""]},"kentauros.actions.UpdateAction":{execute:[1,3,1,""]},"kentauros.actions.UploadAction":{execute:[1,3,1,""]},"kentauros.actions.VerifyAction":{execute:[1,3,1,""]},"kentauros.bootstrap":{ktr_bootstrap:[2,1,1,""],ktr_create_dirs:[2,1,1,""]},"kentauros.build":{Builder:[3,2,1,""],MockBuilder:[3,2,1,""]},"kentauros.build.Builder":{"export":[3,3,1,""],build:[3,3,1,""]},"kentauros.build.MockBuilder":{build:[3,3,1,""]},"kentauros.config":{cli:[4,0,0,"-"],common:[4,0,0,"-"],envvar:[4,0,0,"-"],fallback:[4,0,0,"-"]},"kentauros.config.cli":{get_cli_config:[4,1,1,""]},"kentauros.config.common":{ConfigException:[4,5,1,""],KtrConf:[4,2,1,""]},"kentauros.config.common.KtrConf":{from_file:[4,3,1,""],succby:[4,3,1,""],validate:[4,3,1,""]},"kentauros.config.envvar":{get_env_config:[4,1,1,""]},"kentauros.config.fallback":{get_fallback_config:[4,1,1,""]},"kentauros.conntest":{is_connected:[0,1,1,""]},"kentauros.construct":{rpm_spec:[5,0,0,"-"]},"kentauros.construct.rpm_spec":{RPMSpecError:[5,5,1,""],bump_release:[5,1,1,""],if_release:[5,1,1,""],if_version:[5,1,1,""],spec_bump:[5,1,1,""],spec_preamble_bzr:[5,1,1,""],spec_preamble_git:[5,1,1,""],spec_preamble_url:[5,1,1,""],spec_release_read:[5,1,1,""],spec_version_bzr:[5,1,1,""],spec_version_git:[5,1,1,""],spec_version_read:[5,1,1,""],spec_version_url:[5,1,1,""]},"kentauros.definitions":{ActionType:[0,2,1,""],BuilderType:[0,2,1,""],ConstructorType:[0,2,1,""],InstanceType:[0,2,1,""],KtrConfType:[0,2,1,""],SourceType:[0,2,1,""],UploaderType:[0,2,1,""]},"kentauros.definitions.ActionType":{BUILD:[0,4,1,""],CHAIN:[0,4,1,""],CLEAN:[0,4,1,""],CONFIG:[0,4,1,""],CONSTRUCT:[0,4,1,""],CREATE:[0,4,1,""],EXPORT:[0,4,1,""],GET:[0,4,1,""],PREPARE:[0,4,1,""],REFRESH:[0,4,1,""],STATUS:[0,4,1,""],UPDATE:[0,4,1,""],UPLOAD:[0,4,1,""],VERIFY:[0,4,1,""]},"kentauros.definitions.BuilderType":{MOCK:[0,4,1,""],NONE:[0,4,1,""]},"kentauros.definitions.ConstructorType":{NONE:[0,4,1,""],SRPM:[0,4,1,""]},"kentauros.definitions.InstanceType":{CONFIG:[0,4,1,""],CREATE:[0,4,1,""],NORMAL:[0,4,1,""]},"kentauros.definitions.KtrConfType":{CLI:[0,4,1,""],DEF:[0,4,1,""],DEFAULT:[0,4,1,""],ENV:[0,4,1,""],FALLBACK:[0,4,1,""],FBK:[0,4,1,""],PRJ:[0,4,1,""],PROJECT:[0,4,1,""],SYS:[0,4,1,""],SYSTEM:[0,4,1,""],USER:[0,4,1,""],USR:[0,4,1,""]},"kentauros.definitions.SourceType":{BZR:[0,4,1,""],GIT:[0,4,1,""],LOCAL:[0,4,1,""],NONE:[0,4,1,""],URL:[0,4,1,""]},"kentauros.definitions.UploaderType":{COPR:[0,4,1,""],NONE:[0,4,1,""]},"kentauros.init":{cli:[6,0,0,"-"],env:[6,0,0,"-"]},"kentauros.init.cli":{CLIArgs:[6,2,1,""],get_parsed_cli:[6,1,1,""]},"kentauros.init.cli.CLIArgs":{parse_args:[6,3,1,""]},"kentauros.package":{Package:[7,2,1,""],PackageError:[7,5,1,""]},"kentauros.package.Package":{update_config:[7,3,1,""]},"kentauros.run":{get_action_args:[0,1,1,""],run:[0,1,1,""],run_config:[0,1,1,""]},"kentauros.source":{bzr:[8,0,0,"-"],common:[8,0,0,"-"],git:[8,0,0,"-"],local:[8,0,0,"-"],url:[8,0,0,"-"]},"kentauros.source.bzr":{BzrSource:[8,2,1,""]},"kentauros.source.bzr.BzrSource":{"export":[8,3,1,""],formatver:[8,3,1,""],get:[8,3,1,""],rev:[8,3,1,""],update:[8,3,1,""]},"kentauros.source.common":{Source:[8,2,1,""]},"kentauros.source.common.Source":{"export":[8,3,1,""],clean:[8,3,1,""],formatver:[8,3,1,""],get:[8,3,1,""],prepare:[8,3,1,""],refresh:[8,3,1,""],update:[8,3,1,""]},"kentauros.source.git":{GitSource:[8,2,1,""]},"kentauros.source.git.GitSource":{"export":[8,3,1,""],date:[8,3,1,""],formatver:[8,3,1,""],get:[8,3,1,""],rev:[8,3,1,""],update:[8,3,1,""]},"kentauros.source.local":{LocalSource:[8,2,1,""]},"kentauros.source.local.LocalSource":{formatver:[8,3,1,""],get:[8,3,1,""]},"kentauros.source.url":{UrlSource:[8,2,1,""]},"kentauros.source.url.UrlSource":{get:[8,3,1,""]},"kentauros.upload":{CoprUploader:[9,2,1,""],Uploader:[9,2,1,""]},"kentauros.upload.CoprUploader":{upload:[9,3,1,""]},"kentauros.upload.Uploader":{upload:[9,3,1,""]},kentauros:{"package":[7,0,0,"-"],actions:[1,0,0,"-"],bootstrap:[2,0,0,"-"],build:[3,0,0,"-"],config:[4,0,0,"-"],conntest:[0,0,0,"-"],construct:[5,0,0,"-"],definitions:[0,0,0,"-"],init:[6,0,0,"-"],run:[0,0,0,"-"],source:[8,0,0,"-"],upload:[9,0,0,"-"]}},objnames:{"0":["py","module","Python module"],"1":["py","function","Python function"],"2":["py","class","Python class"],"3":["py","method","Python method"],"4":["py","attribute","Python attribute"],"5":["py","exception","Python exception"]},objtypes:{"0":"py:module","1":"py:function","2":"py:class","3":"py:method","4":"py:attribute","5":"py:exception"},terms:{"abstract":1,"case":8,"class":[0,1,3,4,5,6,7,8,9],"default":[0,1,4,6,8],"enum":[0,1],"export":[0,1,3,8],"function":[0,3,4,5,6,9],"new":5,"return":[0,1,4,5,6,8],"switch":[2,4],"true":[1,8],abbrevi:8,about:[1,4,7,8],access:8,act:4,action:[],action_type_enum:0,actiontyp:[0,1],activ:8,actual:2,add:1,after:[2,8],all:[0,1,4,8],alreadi:[1,4,8],alwai:1,anoth:4,anymor:8,arbitrari:0,argument:[0,6],associ:8,attempt:1,attribut:4,atyp:1,automat:[0,8],avail:[1,8],back:1,base:[0,1,3,4,5,6,7,8,9],basedir:4,been:[0,2,4,8],behind:0,belong:8,between:[1,8],binari:0,bool:1,bootstrap:[],branch:8,build:[],buildact:1,builder:[0,1,3],buildertyp:0,built:[1,3,4],bump:[1,5],bump_releas:5,bumpspec:5,bzr:[],bzrsourc:8,call:0,can:[1,4],chain:[0,1],chainact:1,chang:1,check:[1,8],clean:[0,1,8],cleanact:1,cli:[],cli_arg:[0,6],cli_pars:6,cliarg:[0,6],clone:8,cloud:[0,1],code:[0,1,8],command:[0,1,4,8],commit:8,common:[],conf:[1,7,8],confdir:[2,4,7],config:[],configact:1,configexcept:4,configpars:[1,7],configur:[0,1,2,4,7,8],conftyp:4,connect:[0,8],construct:[],constructact:1,constructor:[0,1],constructortyp:0,contain:[0,1,3,4,5,7,8,9],copi:[1,8],copr:[0,9],coprupload:9,correspond:1,correspondig:8,creat:[0,1,2],createact:1,current:[1,8],data:7,datadir:[0,2,4,8],date:8,datetim:8,def:0,defin:[0,1,5],definiton:0,delet:8,depend:8,describ:0,dest:8,destin:8,determin:[1,4,8],did:1,dir:1,directori:[1,4,8],displai:1,doe:8,doesn:1,don:1,done:1,download:8,dummi:1,dure:4,effect:1,either:8,empti:1,env:[],environ:4,envvar:[],epel:0,eror:4,errmsg:4,error:[5,7],etc:[1,8],evalu:2,even:1,eventu:4,everi:1,everyth:[1,2,8],everywher:0,except:[4,5,7],execut:[0,1],exist:[1,8],explicitli:4,exportact:1,extend:4,fail:[1,8],fallback:[],fals:[1,8],far:4,fbk:0,fedora:0,file:[1,2,4,5,6,8],file_obj:5,filenam:8,filepath:4,follow:[0,1],forc:1,format:[0,5,8],formatv:8,found:[4,5,8],from:[0,1,4,6,8],from_fil:4,further:1,gener:1,get:[0,1,8],get_action_arg:0,get_cli_config:4,get_env_config:4,get_fallback_config:4,get_parsed_cli:6,getact:1,git:[],gitsourc:8,given:[1,4],gone:8,handl:8,hash:8,have:[2,8],helper:5,here:1,hold:[1,7,8],hopefulli:5,host:[0,8],if_releas:5,if_vers:5,includ:[4,7],increas:1,increment:1,index:11,inform:[1,4,7,8],init:[],initialis:[1,6],insid:1,instal:0,instanc:[1,8],instance_typ:6,instancetyp:[0,6],intellig:5,invok:0,is_connect:0,item:4,keep:8,kei:1,kept:8,kind:0,ktr:[0,1,2],ktr_bootstrap:2,ktr_create_dir:2,ktrconf:4,ktrconftyp:0,last:[1,8],later:4,launchpad:8,line:[0,1,4,5],list:4,local:[],localsourc:8,locat:4,look:4,mai:4,main:0,master:8,mean:1,method:[1,3,4,5,6,7,8,9],might:8,mock:0,mockbuild:3,moment:[0,1,7],name:[0,1,7,8],neccesari:8,neccessari:[0,1,8],need:[0,8],neither:8,net:8,nice:[5,8],non:4,none:[0,4,8],nor:8,normal:[0,6,8],number:[1,8],object:[0,1,3,4,6,7,8,9],occur:4,onc:8,onli:[0,1,7,8],option:4,order:4,orig:8,origin:8,other:4,otherwis:1,out:7,overrid:[4,6,8],overridden:1,packagedir:1,packageerror:7,packdir:4,page:11,paramet:[0,1,8],pars:[0,4,6,7],parse_arg:6,parser:6,path:8,pend:1,pkgname:[0,8],place:[1,4],point:[1,8],possibl:0,prepar:[0,1,3,6,8],preparatori:1,prepareact:1,prj:0,process:[4,8],project:0,purpos:8,put:8,quasi:1,rais:4,reachabl:0,reaction:1,read:[4,6],real:1,refer:1,refresh:[0,1,8],refreshact:1,releas:[1,5],remot:8,remov:1,replac:4,repo:8,repodir:8,repositori:[0,1,8],request:8,requst:8,reset:1,respect:[1,8],result:4,rev:8,revis:8,rhel:0,rpm:[0,3,5],rpm_spec:[],rpmdev:5,rpmspecerror:5,run_config:0,save:8,saved_rev:8,script:0,sdir:8,search:11,section:1,self:[4,8],server:[8,9],servic:[0,1],set:[1,4,8],setuptool:0,sever:1,shallow:8,should:[0,1,8],smartli:1,someth:8,sourc:[],sourcetyp:0,spec:[0,4,5],spec_bump:5,spec_preamble_bzr:5,spec_preamble_git:5,spec_preamble_url:5,spec_release_read:5,spec_version_bzr:5,spec_version_git:5,spec_version_read:5,spec_version_url:5,specdir:[2,4],specif:[1,8],specifi:[0,1,2,8],src:3,srpm:0,stage:1,statu:0,statusact:1,step:8,store:[1,8],str:[0,1,8],string:[5,8],structur:7,subclass:[1,8],substitut:8,succbi:4,succe:1,success:[1,8],successfulli:8,support:0,system:[0,8],taglin:5,tarbal:[0,1,4,8],templat:1,temporari:1,termin:1,test:0,thei:1,them:6,theori:0,thi:[0,1,4,7,8],through:1,time:8,tupl:0,type:[0,1,8],unmodifi:0,unsuccess:8,updat:[0,1,8],update_config:7,updateact:1,upload:[],uploadact:1,uploadertyp:0,upstream:8,url:[],urlsourc:8,usabl:4,user:0,usr:0,usual:8,valid:4,valu:[1,4,5,6,7,8],variabl:[1,2,4],verifi:[0,1,4],verifyact:1,version:[1,5,8],via:5,wai:1,went:1,were:[1,8],wget:8,when:[0,1,8],where:8,whether:0,which:[1,4,8],without:1,work:[0,1],write:[1,7],written:1,yet:8,yield:4},titles:["kentauros package","kentauros.actions package","kentauros.bootstrap package","kentauros.build package","kentauros.config package","kentauros.construct package","kentauros.init package","kentauros.package package","kentauros.source package","kentauros.upload package","kentauros","Welcome to kentauros&#8217;s documentation!"],titleterms:{action:1,bootstrap:2,build:3,bzr:8,cli:[4,6],common:[4,8],config:4,conntest:0,construct:5,content:[0,1,2,3,4,5,6,7,8,9],definit:0,document:11,env:6,envvar:4,fallback:4,git:8,indic:11,init:6,kentauro:[0,1,2,3,4,5,6,7,8,9,10,11],local:8,modul:[0,1,2,3,4,5,6,7,8,9],packag:[0,1,2,3,4,5,6,7,8,9],rpm_spec:5,run:0,sourc:8,submodul:[0,4,5,6,8],subpackag:0,tabl:11,upload:9,url:8,welcom:11}})