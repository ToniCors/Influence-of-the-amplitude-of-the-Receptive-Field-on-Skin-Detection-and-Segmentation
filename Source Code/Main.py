#!/usr/bin/env python
# coding: utf-8

# In[1]:


'''La chiusura del thread a volte da problemi: OSError: [WinError 10038] An operation was attempted on something that is not a socket
Suppongo sia un prolema solo di windows, per questo motivo, se vi sono problemi, ho deciso di aumentare il numero della porta server in ascolto di 1
ogni volta che devo testare una nuova istanza (tramite la variabile i)

Per attivare questa procedura di emergenza si deve imporre alla variabile fixed_port_Number il valore False
'''
i=8080
fixed_port_Number= True


'''
Variabile booleana che switcha tra un return della maschera png ed un return della maschera tramitre encoding in base64 di
un np.array a 2 dimensioni
'''
return_output_mask_as_png= False
'''
Nel caso in cui return_output_mask_as_png=True serve un path nel quale mettere le maschere da dare in output.
Questo path serve per fare il dispatching nel metodo do_GET tra le request dirette alla home page e le request dirette alle
immagini (che il browser effettua in automatico quando legge l'attributo src di <img>)
Per evempio ho inserito /outputMasks; che va sostituito con quello reale
'''

SUBPATH_TO_OUTPUT_PNG_MASKS= "/outputMasks"


# In[2]:


from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
import webbrowser
import socket
import cgi
from PIL import Image
import io
import numpy as np

from socketserver import ThreadingMixIn
import threading

import chardet

import base64 


# In[3]:


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_addr = s.getsockname()[0]
print(ip_addr)
s.close()


# In[4]:


home_page= ''' <!DOCTYPE html>
<!--[if lt IE 7 ]> <html dir="ltr" lang="it-IT" class="no-js ie6"> <![endif]-->
<!--[if IE 7 ]>    <html dir="ltr" lang="it-IT" class="no-js ie7"> <![endif]-->
<!--[if IE 8 ]>    <html dir="ltr" lang="it-IT" class="no-js ie8"> <![endif]-->
<!--[if IE 9 ]>    <html dir="ltr" lang="it-IT" class="no-js ie9"> <![endif]-->
<!--[if (gt IE 9)|!(IE)]><!-->
<html dir="ltr" lang="it-IT" class="no-js">
<!--<![endif]-->
<head>
<meta charset="UTF-8">
<!--[if IE]><![endif]-->
<title>Home Page</title>
<meta charset="utf-8" />
<meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />

<meta http-equiv="cache-control" content="max-age=0" />
<meta http-equiv="cache-control" content="no-cache" />
<meta http-equiv="expires" content="0" />
<meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />
<meta http-equiv="pragma" content="no-cache" />


<meta name="viewport"
	content="width=device-width, user-scalable=no, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.5">



<!-- 
<script type="text/javascript"
	src="http://ff.kis.v2.scr.kaspersky-labs.com/9A990825-E6E2-7D40-B622-836E3C87684F/main.js"
	charset="UTF-8"></script>
<script type="text/javascript"
	src="http://ff.kis.v2.scr.kaspersky-labs.com/9A990825-E6E2-7D40-B622-836E3C87684F/main.js"
	charset="UTF-8"></script>
 -->



<!-- Le HTML5 shim, for IE6-8 support of HTML5 elements -->
<!--[if lt IE 9]>
 <script src="//html5shim.googlecode.com/svn/trunk/html5.js"></script>
<![endif]-->




<!--
<link href="http://www.narutogt.it/js/libs/bootstrap/css/behavior-ui-bootstrap.css" media="screen" rel="stylesheet" />
<!---->



<style>
body {
	background: #000000;
}

/*ADDED*/
.ajaximgupload-container {
	position: relative;
	width: 150px;
	height: 100px;
	background-color: #999;
	background-position: center center;
	background-repeat: no-repeat;
	float: left;
}

.ajaximgupload-menu {
	padding: 5px;
	background: #FFFFFF;
	border: 1px #3B5998 solid;
	overflow: visible;
	position: absolute;
	right: 0;
	bottom: 0px;
	color: #3B5998;
	font-family: "lucida grande", tahoma, verdana, arial, sans-serif;
	font-size: 11px;
	opacity: .8;
	box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);
}

.ajaximgupload-computer {
	padding-right: 15px;
	background: url(http://www.narutogt.it/imgs/16x16/upload.gif) no-repeat
		center right #FFFFFF;
	height: 30px;
	position: relative;

	/* Ereditato da .ajaximgupload-menu
color: #3B5998;
font-family: "lucida grande",tahoma,verdana,arial,sans-serif;
font-size: 11px;
*/
}

button {
	display: inline-block;
	padding: 6px 12px;
	margin-bottom: 0;
	font-size: 14px;
	font-weight: normal;
	line-height: 1.42857143;
	text-align: center;
	white-space: nowrap;
	vertical-align: middle;
	-ms-touch-action: manipulation;
	touch-action: manipulation;
	cursor: pointer;
	-webkit-user-select: none;
	-moz-user-select: none;
	-ms-user-select: none;
	user-select: none;
	background-image: none;
	border: 1px solid transparent;
	border-radius: 4px;
	color: #333;
	background-color: #fff;
	border-color: #ccc;
}

/*END ADDED*/


/* ADDED TO CENTER IMG 
https://stackoverflow.com/questions/6490252/vertically-centering-a-div-inside-another-div */

 #ajaximgupload-preview {

  display: flex;
  justify-content: center;
  align-items: center; 

  
 
  /*
  display: table-cell;
  width: 500px;
  height: 500px;
 
 
  //width: 100%; 
  //height: 100%;
 
  vertical-align: middle;
  text-align: center;
   */
}


#immagineOutput {
  /*
  display: inline-block;
  width: 200px; 
  height: 200px;
  */
  
  align-self: center;
}

/* END ADDED TO CENTER IMG */

a#skinClick {
	display: none;
}

#bottom-3 {
	margin: 0px;
	padding: 10px;
	background: #1D1D1D;
}

#sidebar {
	text-align: center;
	float: left;
}

#main-container {
	float: right;
}

#main {
	overflow: hidden;
}

#main ul {
	margin: 0px 10px;
}

#main li {
	margin: 0px 10px;
}

#main img {
	max-width: 320px;
	height: auto;
}

#main iframe {
	/*max-width:320px;*/
	
}

#top .nav-menu {
	margin: 0px -15px 0px -15px;
}

@media ( min-width :768px) {
	.navbar-fixed-top {
		max-width: 750px;
	}
	#logo {
		height: 149px;
	}
	#footer-logo {
		height: 170px;
	}
}

@media ( min-width :992px) {
	.navbar-fixed-top {
		max-width: 970px;
	}
	#logo {
		height: 188px;
	}
	#footer-logo {
		height: 190px;
	}
	#skin {
		/*background: #000000 url('templates/pages/naruto/images/skin1.jpg') no-repeat top right;*/
		/*background: #000000 url('templates/pages/naruto/images/skin_namco_lancio.jpg') no-repeat top right;*/
		background-position: 50% 0px;
	}
	#main img {
		max-width: 640px;
	}
	#main iframe {
		max-width: 640px;
	}
	#skin {
		width: 100%;
		margin: 0px 0px;
		height: 100%;
		padding: 0px;
		z-index: 0;
		position: relative;
	}
	a#skinClick {
		width: 100%;
		height: 100%;
		position: absolute;
		z-index: 0;
		display: block;
	}
}

@media ( min-width :1200px) {
	.navbar-fixed-top {
		max-width: 1170px;
	}
	#logo {
		height: 228px;
	}
}
</style>





<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>

</head>
<body>




	<!-- HERE FORM  -->
	<div class="form-registration">
		<form action="javascript:void(0);" id="form-senting-image"
			enctype="multipart/form-data" autocomplete="off">
			<h6>Modifica dati</h6>


			<script>
					function verificaEdInviaImmagine() {
						var foto = $('#foto');
						var ext = $('#foto').val().split('.').pop().toLowerCase();
						

						if (ext = "" || (ext != "jpg" && ext != "jpeg")) {
							alert("FAILURE FILE NON JPEG");
                            $("#button_to_send").html("<i class='fa fa-floppy-o' aria-hidden='true'></i> Devi prima selezionare un Immagine!");
                            $("#button_to_send").prop("disabled",true);
                            $('#foto').val("");
							return;
						}
                        /* La richiesta deve essere POST, ALTRIMENTI non viene ricevuta dal browser la risposta (NEMMENO DA QUELLI DESKTOP) 
                        CON METODO POST, LA RISPOSTA POST CONTENENTE NELL'SRC DI <img> un link ad un'immagine png presente sul server, viene letto
                        e la successiva request di tipo GET per ottenere l'immagine viene effettuata e completata con successo. Tutto questo anche
                        su un PC desktop diverso da quello HOST del server. 
                        Su mobile invece non funziona, ma il problema non è il metodo GET della prima request (la ajax(), ma la risposta
                        probabilmente, o le successive request get generate da src o la response.
                        
                        Il problema non è legato a CORS REQUEST, IN QUANTO DA UN ALTRO PC DELLA STESSA RETE DEL PC HOST L'IMMAGINE VIENE
                        RICEVUTA E VISUALIZZATA, MENTRE DA UN CELLUARE NELLA STESSA RETE DEL PC HOST NO.
                        
                        
                        DEBUG DI chrome mobile su chrome web tramite chrome://inspect/#devices sul web
                        Il problema è legato al click event di android (su chrome mobile):
                        "[Violation] 'click' handler took 4068ms" in rosso; per questo motivo la response da status code 0.      
                        Al quale è seguito:
                        "XHR failed loading: POST "http://172.19.45.225:8080/imageSent.html"."
                        
                        SU FIREFOX O BROWSER BASATI SU FIREFOX, come AdBlock Browser, non vi è alcun problema. Il problema l'ho
                        riscontrato sinora solo su Chrome.
                        
                        
                        Ho tentato di testare il browser firefox android su firefox desktop, ma non sono riuscito ad installare 
                        e configurare l'inspector: https://developer.mozilla.org/it/docs/Tools/Remote_Debugging/Debugging_Firefox_for_Android_with_WebIDE
                        
                        Update: lancio di web-ide shortcut: https://developer.mozilla.org/it/docs/Tools/WebIDE
                        shift - f8
                        */
						$.ajax({
							type : "POST",
							url : "imageSent.html",
							cache : false,
							contentType : false,
							processData : false,
							/* FORMenctype="multipart/form-data" INDEX*/
							data : new FormData($("#form-senting-image")[0]),
							success : function(risposta, textStatus, jqXHR) {	
								$('#immagineOutput').html(risposta);
                                /* Sistemo l'height; sono presenti comunque, a volte, degli errori di approssimazione di 
                                circa 1 pixel perché i valori sono a volte float approssimati*/
                                var rect1 = document.getElementById("immagineOutput").getBoundingClientRect();
                                console.log("IL DIV " , rect1.top, rect1.right, rect1.bottom, rect1.left);

                                var rect2 = document.getElementById("immagineDiRitorno").getBoundingClientRect();
                                console.log("IMG " , rect2.top, rect2.right, rect2.bottom, rect2.left);
                                
                                $("#immagineOutput").css("height", ($("#immagineOutput").css("height").match(/\d+(\.\d+)?/)[0] - (rect1.bottom - rect2.bottom)) + "px");
                                 /* FINE sistemo l'height */

                            
                                console.error("response responseText  '" + jqXHR.responseText  + "'"); 
                            
								$('#immagineOutput').html(risposta);
								
							},
							error : function(jqXHR, textStatus, errorThrown) { //se la richiesta fallisce
                                /*
								console.error("FAILURE MOTIVATION RESPONSE '" +  jqXHR + "'"); //Ok,un object è ritornato
                                console.error("response textStatus '" + textStatus + "'"); //Ok, la stringa di ritorno ha valore "error"
                                console.error("response statusText '" + jqXHR.statusText + "'");  //Ok, la stringa di ritorno ha valore "error"
                                console.error(" FAILURE MOTIVATION errorThrown '" +  errorThrown + "'"); //Ok, la stringa di ritorno ha valore "", ma non è undefined
                                
                                console.error("response status '" + jqXHR.status + "'"); //Ok il valore è 0
                                console.error("response responseXML  '" + jqXHR.responseXML  + "'"); //Undefined forse perché non è una response XML
                                console.error("response responseText  '" + jqXHR.responseText  + "'"); 
                                console.error("response getAllResponseHeaders()  '" + jqXHR.getAllResponseHeaders()  + "'"); 
                                */
							}
						});
                        /*ERROR, QUI: http://api.jquery.com/jquery.ajax/* response dovrebbe essere un XMLHttpRequestObject 
                        L'oggetto, jqXHR, il primo di success, dovrebbe essere di tipo jqXHR 
                        http://api.jquery.com/jquery.ajax/#jqXHR */
						
					}
				</script>

			<div class="row">
				<div class="col-xs-6">
					<div class="ajaximgupload-container" id="ajaximgupload-preview" style="width: 100%; height: 70vh; background-color: white;">
                        
                        <div id="immagineOutput" style="text-align: center;"></div>
                            <div class="ajaximgupload-menu">
                                <label href="javascript:" class="ajaximgupload-computer" l>
                                    <input type="file" name="immagineJPEG" id="foto" accept="image/jpeg" style="display: none;">Carica immagine JPEG dal tuo device</input>
                                </label>
                             </div>
                         </div>
                             
                      
                      
						<div class="ajaximgupload-loading"></div>
					</div>
				</div>
				<div class="col-xs-12">
					<label>LABELLL</label>

				</div>
			</div>

			<div class="row">
				<div class="col-xs-9" style="text-align: center;">
					<button disabled="disabled" id ="button_to_send" type="submit" value="Salva dati" 
						class="btn btn-lg btn-primary btn-block"
						onclick="verificaEdInviaImmagine()">
						<i class='fa fa-floppy-o' aria-hidden='true'></i> Devi prima selezionare un Immagine!
					</button>
				</div>
			</div>
            
              <input type="hidden" id="divWidth" name="divWidth" value="initialValue">
              <input type="hidden" id="divHeight" name="divHeight" value="initialValue2">
		</form>
	</div>
    
    
    <script> 
    $( document ).ready(function() {
    /*
    console.log("divWidth " + $("#ajaximgupload-preview").css("width").match(/\d+(\.\d+)?/)[0]);
    console.log("divHeight " + $("#ajaximgupload-preview").css("height").match(/\d+(\.\d+)?/)[0]);
    */
   
    $("#divWidth").val("" + $("#ajaximgupload-preview").css("width").match(/\d+(\.\d+)?/)[0]);
    $("#divHeight").val("" + $("#ajaximgupload-preview").css("height").match(/\d+(\.\d+)?/)[0]);
    
    //Sistemo la lunghezza
    $("#immagineOutput").css("width", $("#divWidth").val() + "px");
    //Altezza non è sistemabile cosi, la sistemo nell'ajax
    //$("#immagineOutput").css("height", $("#divHeight").val() + "px");
    
    
    $("#divWidth").val("" + $("#ajaximgupload-preview").css("width").match(/\d+(\.\d+)?/)[0]);
    $("#divHeight").val("" + $("#ajaximgupload-preview").css("height").match(/\d+(\.\d+)?/)[0]);
     
     /*
    console.log("divWidth INPUT HIDDEN " + $("#divWidth").val());
    console.log("divHeight INPUT HIDDEN " + $("#divHeight").val());
    */
    
    
    
    
        //Un altro handler è già presente tramite jquery, i due non vanno in conflitto
        $('#foto').bind("change",function(){ 
            var imgVal = $('#foto').val(); 
            if(imgVal==''){
                $("#button_to_send").html("<i class='fa fa-floppy-o' aria-hidden='true'></i> Devi prima selezionare un Immagine!");
                $("#button_to_send").prop("disabled",true);
            } 
            $("#button_to_send").html("<i class='fa fa-floppy-o' aria-hidden='true'></i> Invia Immagine");
            $("#button_to_send").prop("disabled",false);
           
         }); 


    });
    
    </script>
</body>
</html>
'''


# In[7]:


# NEW SINGLE THREAD FOR EACH REQUEST: https://stackoverflow.com/questions/14088294/multithreaded-web-server-in-python




#Usato per leggere la maschera PNG:
def load_binary(file):
    with open(file, 'rb') as file:
        return file.read()



#https://daanlenaerts.com/blog/2015/06/03/create-a-simple-http-server-with-python-3/
#THIS PC


#Definizione del request handler
# HTTPRequestHandler class

def do_POST_AFTER_RECEIVING_IMAGE(self):
    ctype, pdict = cgi.parse_header(self.headers['content-type'])
    print("ctype " + ctype)
    pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
    #https://stackoverflow.com/questions/31486618/cgi-parse-multipart-function-throws-typeerror-in-python-3
    if ctype == 'multipart/form-data':
        fields = cgi.parse_multipart(self.rfile, pdict)

        immagineJPEG = fields.get("immagineJPEG")
        
        divWidth= fields.get("divWidth")
        print("divWidth " + str(divWidth));
        divHeight= fields.get("divHeight")
        print("divHeight " + str(divHeight));
        
        #toInt
        print(str(divHeight)[3: (len(divHeight)-3)])
        divWidth = float(str(divWidth)[3: (len(divWidth)-3)])
        print("divWidth INT" + str(divWidth))
        
        divHeight = float(str(divHeight)[3: (len(divHeight)-3)])
        print("divHeight INT" + str(divHeight))

        

        print("LUNGHEZZA DEL BYTEARRAY " +  str(len(immagineJPEG[0])))
        print("IMAGE TYPE " + str(type(immagineJPEG[0])))
        
        


        #https://stackoverflow.com/questions/18491416/pil-convert-bytearray-to-image
        #https://stackoverflow.com/questions/11914472/stringio-in-python3
        #im è di tipo: 

        #https://stackoverflow.com/questions/18491416/pil-convert-bytearray-to-image
        #immagineJPEG[0] è un bytearray, come scritto nella istruzione precedente; in questo modo lo converto in un oggetto
        # JpegImageFile. Tutto ciò è sufficiente per scrivere l'immagine su un file, ma non per convertirlo direttamente in un
        # matplotlib.image (senza dover passare per la scrittura e lettura su file)
        im = Image.open(io.BytesIO(immagineJPEG[0]))
        
        the_encoding = chardet.detect(immagineJPEG[0])['encoding']
        if the_encoding is not None:
            print("ENCODING = " + the_encoding)

        imageNPArray = np.array(im)

        print (imageNPArray)
        print ("imageNPArray shape " + str(imageNPArray.shape))
        
        
        # INTERAZIONE CON RANDOM FOREST
        
        ''' QUI È possibile invocare tutti i metodi del RandomForestClassifier per fare le predizioni, avendo in input
        "imageNPArray", che è un numpy.array di shape image_height x image_width x 3
        '''
        
        
        
        '''
        Al termine, se return_output_mask_as_png è impostata a true, si caricherà la maschera da dare in output all'utente.
            In particolare, in questo caso, assumono particolare rilevanza le variabili  PATH_TO_PNG_MASK e "MASK_FILENAME":
            la prima è una variabile "di servizio" che serve ad indicare il subpath che, partendo dalla directory attuale, conduce
            a quella nella quale sono storate le maschere png di output da dare agli utenti. 
                Questa variabile serve per il dispatching all'interno del metodo "do_GET" tra le request che sono dirette 
                alla home_page e le request che sono invece dirette ad un'immagine PNG rappresentante una maschera di output 
                (le request di quest'ultimo tipo sono automaticamente generate dal browser, in maniera asincrona, subito 
                dopo aver letto l'attributo "src" di <img>).
            
                La seconda invece è il nome della maschera vero e proprio,che ovviamente deve essere identico rispetto a 
                quello usato nell'effettuare lo storage su disco della maschera di output.
            
                  
            
        Altrimenti, se return_output_mask_as_png =False, un'encoding diretto della maschera viene passato nell'attributo
        src di <img>, senza necessità di salvataggio dell'immagine sul disco.
        
        '''
        

       
        #Se non richiedo la maschera in output come png, ma la voglio diretta con codifica base64 
        if not return_output_mask_as_png: 
            #output zone
            #da cambiare: lo pongo, per testare, = a byte di valore 0 o 1 contigui in diagonale
            #Nell'implementazione reale andrebbe posto = all'np.array rappresentante la maschera da dare in output
           
        
            outputNPArray=np.empty([im.height, im.width, 3], np.uint8)
            print("OUTPUT NPARRAY SHAPE " + str(outputNPArray.shape))
            for i in range (im.height):
                for j in range (im.width):
                    if (i+j)%2==0:
                        outputNPArray[i][j][0]=255
                        outputNPArray[i][j][1]=255
                        outputNPArray[i][j][2]=255
                    else: 
                        outputNPArray[i][j][0]=0
                        outputNPArray[i][j][1]=0
                        outputNPArray[i][j][2]=0
            
            
            #Classe PIL.Image.Image
            outputImagePILImageImageClass= Image.fromarray(outputNPArray)
            #outputImagePILImageImageClass.save("testSave.png")
            '''
            https://stackoverflow.com/questions/33101935/convert-pil-image-to-byte-array           
            COME OTTENERE I BYTES FROM AN IMAGE      
            '''
            roiImg = outputImagePILImageImageClass.crop()
            imgByteArr = io.BytesIO()
            roiImg.save(imgByteArr, format='PNG')
            outputImageBytes = imgByteArr.getvalue()

            
            print("lenoutputImageBytes = " + str(len(outputImageBytes)) + " shape dell'nparray = " + str(outputNPArray.shape))
            
            print("stringaOutput = " + str(outputImageBytes))
       
            
            
            cosaStoRispondendo = base64.b64encode(outputImageBytes)
            
            #cosaStoRispondendo = base64.b64encode(immagineJPEG[0])
            cosaStoRispondendo= str(cosaStoRispondendo)

            cosaStoRispondendo= cosaStoRispondendo[2:]
            cosaStoRispondendo= cosaStoRispondendo[: len(cosaStoRispondendo)-1]
            
            #Scelgo la width e la height dell'immagine da inviare, in relazione alle dimensioni dell'immagine in input ed alle
            # dimensioni del div di output (la zona centrale con background bianco) sul device
            
            imageWidth= im.width
            imageHeight= im.height        
            if imageWidth > divWidth:
                scalingFactor = imageWidth/divWidth
                print("INITIAL STATE BEFORE SCALING BY WIDTH IM.width = " + str(imageWidth) + " divWidth = " + str(divWidth) + " scalingFactor " + str(scalingFactor))
                #dovrebbe matchare con divWidth
                imageWidth = imageWidth/scalingFactor 
                imageHeight = imageHeight/scalingFactor 
                print("SCALING BY WIDTH BECAUSE EXCEEDED THE LIMIT, NEW SIZES: NEW WIDTH IS " + str(imageWidth) + " new height is " + str(imageHeight))

            if imageHeight > divHeight:
                scalingFactor = imageHeight/divHeight
                print("INITIAL STATE BEFORE SCALING BY HEIGHT IM.height = " + str(imageHeight) + " divHeight = " + str(divHeight) + " scalingFactor " + str(scalingFactor))      
                imageWidth = imageWidth/scalingFactor 
                #dovrebbe matchare con divHeight
                imageHeight = imageHeight/scalingFactor 
                print("SCALING BY HEIGHT BECAUSE EXCEEDED THE LIMIT, NEW SIZES: NEW WIDTH IS " + str(imageWidth) + " new height is " + str(imageHeight))
            
            #Da riattivare
            message = "<img id ='immagineDiRitorno' height='" + str(imageHeight) + "' width = '" + str(imageWidth) +  "' src='data:image/jpg;base64, " +  cosaStoRispondendo + "' />" 
            #message = "<img src ='" + fileSystemPathToImage + "' height='" + str(im.height) + "' width = '" + str(im.width) + "' >"
            # Write content as utf-8 data
        
        #Se ho richiesto l'immagine in output come png
        else:
            print("VOGLIO IN OUTPUT IMMAGINE IN FORMATO PNG ")
            #Inserito nella seguente variabile valore di prova, da sostituire con il FILENAME della maschera PNG (all'interno del subpath delle
            #maschere)
            MASK_FILENAME= "/100X2000PNG.png"
            
            #SUBPATH_TO_OUTPUT_PNG_MASKS è stata definita nel primo blocco di istruzioni in alto a questo documento
            PATH_TO_PNG_MASK =  SUBPATH_TO_OUTPUT_PNG_MASKS + MASK_FILENAME
            
            
             #Scelgo la width e la height dell'immagine da inviare, in relazione alle dimensioni dell'immagine in input ed alle
            # dimensioni del div di output (la zona centrale con background bianco) sul device
            
            imageWidth= im.width
            imageHeight= im.height        
            if imageWidth > divWidth:
                scalingFactor = imageWidth/divWidth
                print("INITIAL STATE BEFORE SCALING BY WIDTH IM.width = " + str(imageWidth) + " divWidth = " + str(divWidth) + " scalingFactor " + str(scalingFactor))
                #dovrebbe matchare con divWidth
                imageWidth = imageWidth/scalingFactor 
                imageHeight = imageHeight/scalingFactor 
                print("SCALING BY WIDTH BECAUSE EXCEEDED THE LIMIT, NEW SIZES: NEW WIDTH IS " + str(imageWidth) + " new height is " + str(imageHeight))

            if imageHeight > divHeight:
                scalingFactor = imageHeight/divHeight
                print("INITIAL STATE BEFORE SCALING BY HEIGHT IM.height = " + str(imageHeight) + " divHeight = " + str(divHeight) + " scalingFactor " + str(scalingFactor))      
                imageWidth = imageWidth/scalingFactor 
                #dovrebbe matchare con divHeight
                imageHeight = imageHeight/scalingFactor 
                print("SCALING BY HEIGHT BECAUSE EXCEEDED THE LIMIT, NEW SIZES: NEW WIDTH IS " + str(imageWidth) + " new height is " + str(imageHeight))
            
            message = "<img id ='immagineDiRitorno' height='" + str(imageHeight) + "' width = '" + str(imageWidth) + "' src='" + PATH_TO_PNG_MASK + "' />" 
        print("FINE IMAGE REQUEST! ")    
        self.wfile.write(bytes(message, "utf8"))


class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
    
    #GET usato per la home_page
    def do_GET(self):
        print("PATH IS " + self.path )
       
        #Richiesta l'home Page
        if self.path == '/':    
            print("Home page requested ")
            #print("PATH IS " + self.path)
            # Send response status code
            self.send_response(200)

            # Send headers
            self.send_header('Content-type','text/html')
            self.end_headers()

            # Send message back to client
            #message = "<html><body><b>ciaone</b></body></html>"
            message = home_page
            # Write content as utf-8 data
            self.wfile.write(bytes(message, "utf8"))
            
        if self.path.startswith(SUBPATH_TO_OUTPUT_PNG_MASKS):
            print("STARTS WITH PNG IMAGE OK, tutto il path completo è " + self.path)
            self.wfile.write(load_binary(self.path[1:]))
            
        if self.path == '/imageSent.html':          
            do_POST_AFTER_RECEIVING_IMAGE(self)
        return

    
    #POST USATO PER LA AJAX REQUEST contenente L'IMMAGINE
    def do_POST(self):     
        print("NEL DO_POST: PATH IS " + self.path)
        if self.path == '/imageSent.html':          
            do_POST_AFTER_RECEIVING_IMAGE(self)
        return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""  
    pass
    
    
  
                         

#HOST_NAME = '172.16.60.6' # !!!REMEMBER TO CHANGE THIS!!!
HOST_NAME = ip_addr # !!!REMEMBER TO CHANGE THIS!!!
#httpsHOST_NAME://stackoverflow.com/questions/16928112/permissionerror-errno-13-permission-denied-python
if fixed_port_Number:
    PORT_NUMBER = 8080 
else:
    PORT_NUMBER = i
    i=i+1


#Funzione per fare il run di un server oggetto testHTTPServer_RequestHandler, che viene poi ritornato al chiamante
def create_server():
    print('creating server...')
    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    print("PORT_NUMBER ACTUAL = " + str(PORT_NUMBER))
    server_address = (HOST_NAME, PORT_NUMBER)
    #creo il server sulla porta e sull'host indicati, con il request_Handler definito sopra
    #httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print("SERVER_ADDRESS " + str(server_address) )
    httpd = ThreadedHTTPServer(server_address, testHTTPServer_RequestHandler)
    #ritorno il server http al chiamante
    
    
    return httpd


def run_server(server_instance_to_run):
    print('running server...')
    server_instance_to_run.serve_forever()
    
def stop_server(server_instance_to_stop):
    server_instance_to_stop.server_close()
    print('server stopped...')




    
    
    
#Lancio il server su un altro Thread
class ServerThread(Thread):
    
   
    def __init__(self):
        super(ServerThread, self).__init__()
        self.__server_instance = create_server()
    
    def run(self):
        super(ServerThread, self).run()
        run_server(self.__server_instance)
        
    
    def close_server(self):
        print(self.__server_instance)
        stop_server(self.__server_instance)
        return self.__server_instance
        
#Chiudo il precedente
#https://stackoverflow.com/questions/1592565/determine-if-variable-is-defined-in-python
if 'thread' in globals() and thread is not None:
    print("THREAD NOT NONE")
    thread.close_server()

        
thread = ServerThread()
thread.start()

url= "http://" +HOST_NAME+ ":" + str(PORT_NUMBER)
print(url)
# generate an URL
webbrowser.open(url)




'''La chiusura del thread a volte da problemi: OSError: [WinError 10038] An operation was attempted on something that is not a socket
Suppongo sia un prolema solo di windows, per questo motivo, se vi sono problemi, ho deciso di aumentare il numero della porta server in ascolto di 1
ogni volta che devo testare una nuova istanza (tramite la variabile i)

Per attivare questa procedura di emergenza si deve imporre alla variabile fixed_port_Number il valore False
'''
thread.close_server()


# In[ ]:


'''code to execute prediction'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.image as img
import ast
import math
import pickle
from sklearn.ensemble import RandomForestClassifier as rfc
import pandas as pd
from math import *


class Predictor(object):


    def __init__(self, classifier_path, block_size):
        self.classifier = pickle.load(open(classifier_path, 'rb'))
        self.block_size = block_size


    def get_hue(r, g, b):

        nr = r/255
        ng = g/255
        nb = b/255

        hue = 0.0

        mi = min(min(nr, ng), nb);
        ma = max(max(nr, ng), nb);

        if (mi == ma):
            return hue

        if (ma == nr):
            hue = (ng - nb) / (ma - mi)

        elif (ma == ng):
            hue = 2.0 + (nb - nr) / (ma - mi)

        else:
            hue = 4.0 + (nr - ng) / (ma - mi)

        hue = hue * 60

        if (hue < 0):
            hue = hue + 360

        hue = round(hue)
        return hue

    def feature_extractor(image):
        height = len(image)
        width = len(image[0])

        features_image = []

        for i in range(height):
            row = []
            for j in range(width):

                r = image[i][j][0]
                g = image[i][j][1]
                b = image[i][j][2]

                y = (.299*r + .587*g + .114*b)
                cb = (128 -.168736*r -.331364*g + .5*b)
                cr = (128 +.5*r - .418688*g - .081312*b)

                values = [y, cb, cr, get_hue(r, g, b), r/255]
                row.append(values)
            features_image.append(row)

        return features_image

    def get_block(section, block_size):
        block = np.asarray([])
        for i in range(block_size):
            for j in range(block_size):
                block = np.insert(block, len(block), section[i][j], 0)
        return np.asarray(block)

    def get_blocks(image, mask, block_size):

        height = len(image)
        width = len(image[1])

        i_blocks = np.asarray([])
        m_blocks = np.asarray([])

        n_horizontal_blocks = int(math.floor(width/block_size))
        n_vertical_blocks = int(math.floor(height/block_size))

        for i in range(n_horizontal_blocks):
            for j in range(n_vertical_blocks):
                b = get_block(image[(s*i) : (s*(i+1))][(s*j) : (s*(j+1))])
                m = get_block(mask[(s*i) : (s*(i+1))][(s*j) : (s*(j+1))])

                i_blocks.append(b)
                m_blocks.append(m)

        return i_blocks, m_blocks

    def get_separate_blocks(items, block_size, avoid = []):

        blocks = []
        for k in range(len(items)):
            if k in avoid:
                continue
            item = np.asarray(items[k])
            height = len(item)
            width = len(item[1])
            n_horizontal_blocks = int(math.floor(width/block_size))
            n_vertical_blocks = int(math.floor(height/block_size))

            for i in range(n_vertical_blocks):
                for j in range(n_horizontal_blocks):
                    section = np.asarray(item[(i*block_size) : ((i+1)*block_size), (j*block_size) :((j+1)*block_size)])

                    blocks.append(get_block(section, block_size))

        return np.asarray(blocks)

    def build_empty_mask(n_rows, n_cols):
        mask = np.zeros((n_rows, n_cols), dtype=int)
        return mask


    def build_output_mask(n_rows, n_cols, predictions, block_size, treshold):

        out_mask = build_empty_mask(n_rows, n_cols)

        for i in range(n_rows-block_size):
            for j in range(n_cols-block_size):
                p = predictions[(i*(n_cols-block_size))+j]
                out_mask[i:(i+block_size), j:(j+block_size)] = out_mask[i:(i+block_size), j:(j+block_size)] + p

        for i in range(n_rows):
            for j in range(n_cols):
                if out_mask[i, j] >= treshold:
                    out_mask[i, j] = 255
                else:
                    out_mask[i, j] = 0
        return out_mask

    def build_output_mask_separate(n_rows, n_cols, predictions, block_size):

        n_horizontal_blocks = int(math.floor(n_cols/block_size))
        n_vertical_blocks = int(math.floor(n_rows/block_size))

        height = n_vertical_blocks*block_size
        width = n_horizontal_blocks*block_size

        out_mask = np.zeros((n_vertical_blocks*block_size, n_horizontal_blocks*block_size), int)


        for i in range(n_vertical_blocks):
            for j in range(n_horizontal_blocks):
                p = predictions[(i*n_horizontal_blocks)+j]
                out_mask[(i*block_size) : ((i+1)*block_size), (j*block_size) :((j+1)*block_size)] =  np.reshape(p, (block_size, block_size))

        return height, width, out_mask

    def scale_labels(labels, block_size):
        new_labels = []

        for k in range(len(labels)):
            c = []
            for i in range(block_size*block_size):
                if labels[k][i] == 0:
                    c.append(0)
                else :
                    c.append(1)
            new_labels.append(c)
        return np.asarray(new_labels)

    def add_border(vertical_diff, horizontal_diff, image):
        height = len(image)
        width = len(image[0])
        mask = np.zeros((height+(2*vertical_diff), width+(2*horizontal_diff), 5), int)
        mask[vertical_diff:height+vertical_diff, horizontal_diff: width+horizontal_diff] = image
        return mask

    def join_predictions(p1, p2, height, width, h_dif, v_dif, block_size, treshold):
        a, b, mask1 = build_output_mask_separate(height+v_dif, width+h_dif, p1, block_size)
        a, b, mask2 = build_output_mask_separate(height+v_dif, width+h_dif, p2, block_size)

        mask1 = mask1[v_dif:height+v_dif, h_dif:width+h_dif]
        mask2 = mask2[0:height, 0:width]

        mask = mask1 + mask2

        for i in range(height):
            for j in range(width):
                if mask[i, j] == 2:
                    mask[i, j] = 255
                else:
                    mask[i, j] = 0
        return mask

    def get_prediction(classifier, image, block_size):
        height=len(image)
        width=len(image[0])

        horizontal_difference = block_size - (width % block_size)
        vertical_difference = block_size - (height % block_size)

        image = add_border(vertical_difference, horizontal_difference, image)

        b1 = get_separate_blocks([image[0:height+vertical_difference, 0:width+horizontal_difference]], block_size)
        b2 = get_separate_blocks([image[vertical_difference:height+(2*vertical_difference), horizontal_difference:width+(2*horizontal_difference)]], block_size)

        p1 = classifier.predict(b1)
        p2 = classifier.predict(b2)

        return join_predictions(p1, p2, height, width, horizontal_difference, vertical_difference, block_size, 2)

    def get_predictions(classifier, images, block_size):
        l = len(images)
        predictions = []
        for i in range(l):
            predictions.append(get_prediction(classifier, images[i], block_size))
        return predictions

    def predict(image_path):
        image = img.imread(image_path)
        image_features = features_extractor(image)
        prediction = get_predictions(self.classifier, [image_features], self.block_size)
        plt.imsave("Predizioni/test.bmp", prediction, cmap=cm.gray)

k = Predictor("RFC_BS_10.sav",10)
k.predict("a.jpg")

