from segment import Segment

if __name__ == "__main__":
    spliter = Segment()
    spliter.segment(url="http://www.sej.co.jp/", output_folder="data/seven", is_output_images=True)
