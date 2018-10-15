from segment import Segment

if __name__ == "__main__":
    spliter = Segment()
    spliter.segment(url="https://tokyo2020.org/en/", output_folder="data/tokyo2020", is_output_images=True)
