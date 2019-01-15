from segment import Segment
import datetime
if __name__ == "__main__":
    spliter = Segment()
    print(datetime.datetime.now())
    spliter.segment(url="https://tokyo2020.org/en/", output_folder="data/tokyo2020", is_output_images=True)
    print(datetime.datetime.now())