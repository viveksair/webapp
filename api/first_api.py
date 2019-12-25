import json
from flask import Flask, Response, abort, request, render_template, send_from_directory
import imageio
import os, sys
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

# Create an S3 client
s3 = boto3.resource('s3')

mybucket = "gifblue"


APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route("/init")
def index():
    return render_template("upload.html")


@app.route("/upload", methods=["POST"])
def upload():
    # folder_name = request.form['superhero']
    '''
    # this is to verify that folder to upload to exists.
    if os.path.isdir(os.path.join(APP_ROOT, 'files/{}'.format(folder_name))):
        print("folder exist")
    '''
    target_local = '.gif'
    target = os.path.join(APP_ROOT, 'images')
    target_local_gif = target + target_local

    print(target)
    print(target_local_gif)

    if not os.path.isdir(target):
        os.mkdir(target)
    print("input location")
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        reader = imageio.get_reader(filename)
        fps = reader.get_meta_data()['fps']


        """
        # This is to verify files are supported
        ext = os.path.splitext(filename)[1]        
        if (ext == ".jpg") or (ext == ".mp4"):
            print("File supported moving on...")
        else:
            render_template("Error.html", message="Files uploaded are not supported...")
        """

        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        destination_local_gif = destination + target_local
        print(destination_local_gif)
        upload.save(destination)

        writer = imageio.get_writer(destination_local_gif, fps=fps)
        for i,im in enumerate(reader):
            sys.stdout.write("\rframe {0}".format(i))
            sys.stdout.flush()
            writer.append_data(im)
        print("\r\nFinalizing...")
        writer.close()
        print("Done.")
        print(destination)
        print(destination_local_gif)

        object_name_video = 'videos/' + filename
        object_name_gif = 'gifs/' + filename + '.gif'
        
        # s3 bucket upload

        print(object_name_video)
        print(object_name_gif)

        s3.meta.client.upload_file(destination, 'gifblue', object_name_video) #video
        s3.meta.client.upload_file(destination_local_gif, 'gifblue', object_name_gif) #gif

        """     
        send to s3 
        send to database

        """
    # return send_from_directory("images", filename, as_attachment=True)
    return render_template("complete.html", image_name=filename)

@app.errorhandler(404)
def not_found(e):
    return '', 404

@app.route('/gifupload')
def gifupload():
    """http://0.0.0.0:8080/gifupload?inputpath=SampleVideo_1280x720_1mb.mp4&targetFormat=.gif"""
    
    if 'inputpath' and 'targetFormat' in request.args:
        input_local = request.args['inputpath']
        target_local = request.args['targetFormat']
        response = Response(
            'Hello ' + input_local +' '+ target_local , status=200, mimetype=JSON_MIME_TYPE)
        outputpath = os.path.splitext(input_local)[0] + target_local
        print("converting\r\n\t{0}\r\nto\r\n\t{1}".format(input_local, outputpath))
        
        reader = imageio.get_reader(input_local)
        fps = reader.get_meta_data()['fps']
        writer = imageio.get_writer(outputpath, fps=fps)
        for i,im in enumerate(reader):
            sys.stdout.write("\rframe {0}".format(i))
            sys.stdout.flush()
            writer.append_data(im)
        print("\r\nFinalizing...")
        writer.close()
        print("Done.")
        
        """
        send to s3 
        videos
        S3.Bucket(BUCKET).upload_file(destination, BUCKET"/videos")
        S3.Bucket(BUCKET).upload_file(destination_local_gif, BUCKET"/videos")

        send to database

        """
        return response
    else:
        # return 'Hello John Doe'
        response = Response(
            json.dumps(books), status=200, mimetype=JSON_MIME_TYPE)
        return response