import pathlib

import Quartz
import Vision
from Cocoa import NSURL
from Foundation import NSDictionary
# needed to capture system-level stderr
from wurlitzer import pipes


def image_to_text(img_path, lang="eng"):
    input_url = NSURL.fileURLWithPath_(img_path)

    with pipes() as (out, err):
    # capture stdout and stderr from system calls
    # otherwise, Quartz.CIImage.imageWithContentsOfURL_
    # prints to stderr something like:
        input_image = Quartz.CIImage.imageWithContentsOfURL_(input_url)

    vision_options = NSDictionary.dictionaryWithDictionary_({})
    vision_handler = Vision.VNImageRequestHandler.alloc().initWithCIImage_options_(
        input_image, vision_options
    )
    results = []
    handler = make_request_handler(results)
    vision_request = Vision.VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler)
    error = vision_handler.performRequests_error_([vision_request], None)
    vision_request.dealloc()
    vision_handler.dealloc()

    return results

def make_request_handler(results):
    """ results: list to store results """
    if not isinstance(results, list):
        raise ValueError("results must be a list")

    def handler(request, error):
        if error:
            print(f"Error! {error}")
        else:
            observations = request.results()
            for text_observation in observations:
                recognized_text = text_observation.topCandidates_(1)[0]
                results.append([recognized_text.string(), recognized_text.confidence()])
    return handler


def main():
    import sys
    import pathlib

    img_path = pathlib.Path(sys.argv[1])
    if not img_path.is_file():
        sys.exit("Invalid image path")
    img_path = str(img_path.resolve())
    results = image_to_text(img_path)
    print(results)


if __name__ == "__main__":
    main()
