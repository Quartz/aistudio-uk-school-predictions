import aiohttp
import asyncio
import uvicorn
import random
from fastai import *
from fastai.text import *
from io import BytesIO, StringIO
import matplotlib.cm as cm
from tika import parser
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

export_file_url = 'https://qz-aistudio-jbfm-scratch.s3.amazonaws.com/schools3.pkl'
export_file_name = 'schools3.pkl'

classes = ['last', 'not_last']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X_Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))

async def download_file(url, dest): # Download the pickled model
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)

async def setup_learner(): # Load learner for predictions
    await download_file(export_file_url, path / export_file_name)
    try:
        test = ItemList.from_csv(path='app/',csv_name='last_report_test_sample.csv')
        learn = load_learner(path, export_file_name,test) # Replace path with path of file
        learn.model = learn.model.module # must reference module since the learner was wrapped in nn.DataParallel
        preds = learn.get_preds(ds_type=DatasetType.Test)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print (e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
    else:
        raise

loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()

@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())

@app.route('/analyze', methods=['POST'])
async def predict(request):
    pdf_data = await request.form()
    if isinstance(pdf_data['file'],str):
        pdf = pdf_data['file'] # Get the link
        isLink= True
        if pdf_data['to_email']:
            sendEmail = True
            emails = pdf_data['to_email']
            from_email = pdf_data['from_email']
        else:
            sendEmail = False
    else:
        pdf_bytes = await(pdf_data['file'].read())
        pdf = BytesIO(pdf_bytes)
        isLink, sendEmail = False, False
    try:
        if isLink:
            text = parser.from_file(pdf)['content'] # Pull down file from link
        else:
            text = parser.from_buffer(pdf)['content']
        text = text.replace('\n',' ')
        prediction = learn.predict(text)
        tensor_label = prediction[1].item()
        if tensor_label == 0:
            prob = prediction[2][0].item()
            res = "Result: " + str(prediction[0]) + " - this school may be in danger of closing"
        else:
            prob = prediction[2][1].item()
            res = "Result: " + str(prediction[0]) + " - this school is not in danger of closing"
        txt_ci = TextClassificationInterpretation.from_learner(learn=learn,ds_type=DatasetType.Test)
        # attention = txt_ci.html_intrinsic_attention(text,cmap=cm.Purples)
        text, attn = txt_ci.intrinsic_attention(text)
        text = text.text.split()
        attn = to_np(attn)
        tups = []
        for i in range(len(text)):
            tups.append((text[i],attn[i]))
        tups = sorted(tups, key=lambda x: x[1], reverse=True)
        i,j,top15words=0,0,[]
        tokens = ['xxunk','xxpad','xxbos','xxfld','xxmaj','xxup','xxrep','xxwrep','ofsted','piccadilly'] # leave out tokens since we can't decode them
        while i < 15 and j < len(tups):
            if tups[j][0] not in tokens:
                top15words.append(tups[j][0])
                i+=1
            j+=1
        top15words_string = ""
        for word in top15words:
            top15words_string = top15words_string + word + "<br>"
    except Exception as e:
        prob, attention = "",""
        res = "Sorry, we ran into an error! Please check the file type of the report you submitted. This app only supports .pdf and .txt files."
        print (e)
        raise
    finally:
        if sendEmail: # if sendEmail == True, send email with Twilio
            if str(prediction[0]) == 'last':
                message = Mail(
                from_email=from_email,
                to_emails=emails,
                subject='Testing School Classifier',
                html_content="Hey there! We ran into an interesting school report, and by our calculations, this could possibly be the school's final report before it closes. Here's the link to the report: " + pdf + "<br><br>And here are a few words that stood out to us: <br>" + top15words_string
                )
                try:
                    sg = SendGridAPIClient(os.environ.get('apiKey'))
                    response = sg.send(message)
                    print (response.status_code)
                    print (response.body)
                    print (response.headers)
                except Exception as e:
                    print(str(e))
            print ("Class: " + str(prediction[0]))
            print ("Probability: " + str(prob))
        return JSONResponse({'result': res, 'probability': prob, 'attention': top15words})

if __name__ == '__main__':
    if 'serve' in sys.argv: uvicorn.run(app=app, host='0.0.0.0', port=5042, log_level="info")
