from PIL import Image, ImageFilter, ImageEnhance
import pytesseract

def imageToString(image_file):
    
    pre_processed_image = pre_process_image(image_file)
    image_test = pytesseract.image_to_string(pre_processed_image, lang='kor');
    return image_test


def pre_process_image(image_file):
    image = Image.open(image_file)
    image = image.resize((800, 600))  # 이미지 크기 조정
    image = image.filter(ImageFilter.GaussianBlur(radius=1)) # 가우시안 블러
    #TODO: 미디언 필터와 비교
    image = image.filter(ImageFilter.EDGE_ENHANCE)
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(2.0) 
    image = image.convert('L')  # 흑백으로 변환
    image = image.point(lambda p: p > 128 and 255)  # 이진화
    return image

