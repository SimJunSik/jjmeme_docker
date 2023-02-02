import google_drive_lib
import notion_lib
import s3_lib
import os
import pymysql
import models
import requests
import time

from PIL import Image
from io import BytesIO
from pprint import pprint
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

pymysql.install_as_MySQLdb()

class MemeDBUploader():
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST","localhost")
    DB_PORT = os.getenv("DB_PORT", 3306)
    DB_DATABASE = os.getenv("DB_DATABASE")

    DATABASE_URL = f"mysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    engine = create_engine(DATABASE_URL, encoding="utf-8", pool_recycle=3600)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

    @staticmethod
    def google_drive_to_notion(target_folder_names):
        # google drive 에서 파일 목록 받아오기
        files = google_drive_lib.get_files(target_folder_names)

        # 받아온 파일 목록 다운로드 받기
        google_drive_lib.download_from_google_drvie(files)

        # 다운로드 받은 파일들 s3 업로드
        s3_lib.upload_image()

        # s3 에 올라가있는 이미지 목록 가져오기
        obj_url_list = s3_lib.get_obj_url_list()
        print(obj_url_list)

        # s3 에서 가져온 목록 notion db 에 업로드 하기
        notion_db_title_list = notion_lib.get_title_list()
        base_url = "https://jjmeme-bucket-2.s3.amazonaws.com/"
        for obj_url in obj_url_list:
            name, ext = os.path.splitext(obj_url)
            name = name.replace(base_url, "")
            print(name, ext, obj_url)
            
            if name not in notion_db_title_list:
                notion_lib.create(name, ext, obj_url.replace(" ", "%20"))
            else:
                print("Already exists")

    @staticmethod
    def notion_to_rdb():
        db = MemeDBUploader.db_session()

        # admin account
        if db.query(models.ACCOUNT).filter_by(name="thismeme_admin").count() == 0:
            account = models.ACCOUNT(email="thismeme@gmail.com", name="thismeme_admin", password="password")
            db.add(account)
            db.flush()
            db.refresh(account)
        else:
            account = db.query(models.ACCOUNT).filter_by(name="thismeme_admin").first()

        # notion 에서 데이터 목록 가져오기
        results = notion_lib.read()
        print(f"총 데이터 수: {len(results)}")
        time.sleep(3)

        # Meme column 리스트
        meme_column_list = ["밈 제목", "밈 설명(optional)", "URL", "기존 태그"]

         # 태그 카테고리 리스트
        tag_category_list = [key for key in results[0]['properties'].keys() if key not in meme_column_list]
        print(tag_category_list)

        for result in results:
            data = result['properties']
            pprint(data)

            tags_dict = {}
            for key in data.keys():
                if key in tag_category_list:
                    tags = [tag['name'] for tag in data[key]['multi_select']]
                    tags_dict[key] = tags
                else:
                    try:
                        name = data['밈 제목']['title'][0]['plain_text']
                    except:
                        name = "제목을 지어주세요 :("
                    
                    try:
                        description = data['밈 설명']['rich_text']['plain_text']
                    except:
                        description = ""

                    try:
                        url = data['URL']['url']
                    except:
                        url = ""
            print(tags_dict)

            # 밈 생성
            if db.query(models.MEME).filter_by(name=name).count() == 0:
                meme = models.MEME(name=name, description=description, account_id=account.account_id)
                db.add(meme)
                db.flush()
                db.refresh(meme)
            else:
                meme = db.query(models.MEME).filter_by(name=name).first()

            for category_name in tags_dict.keys():
                # 카테고리 생성 혹은 가져오기
                if db.query(models.CATEGORY).filter_by(name=category_name).count() == 0:
                    category = models.CATEGORY(name=category_name)
                    db.add(category)
                    db.flush()
                    db.refresh(category)
                else:
                    print("Already exists CATEGORY")
                    category = db.query(models.CATEGORY).filter_by(name=category_name).first()

                # 태그 생성
                tags = tags_dict[category_name]
                for tag_name in tags:
                    if db.query(models.TAG).filter_by(name=tag_name, category_id=category.category_id).count() == 0:
                        tag = models.TAG(name=tag_name, category_id=category.category_id)
                        db.add(tag)
                        db.flush()
                        db.refresh(tag)

                        meme_tag = models.MEME_TAG(meme_id=meme.meme_id, tag_id=tag.tag_id, account_id=meme.account_id)
                        db.add(meme_tag)
                    else:
                        print("Already exists TAG")

            # 이미지 생성
            if url:
                if db.query(models.IMAGE).filter_by(image_url=url).count() == 0:
                    response = requests.get(url)
                    try:
                        img = Image.open(BytesIO(response.content))

                        image = models.IMAGE(image_url=url, width=img.width, height=img.height, 
                                                meme_id=meme.meme_id, account_id=meme.account_id)
                        db.add(image)
                        db.flush()
                        db.refresh(image)
                    except:
                        continue
                else:
                    image = db.query(models.IMAGE).filter_by(image_url=url).first()

        db.commit()
        db.close()


if __name__ == "__main__":
    # target_folder_names = ["추가 조사한 무한도전 짤", "2022125_12958_박명수 짤"]
    # MemeDBUploader.google_drive_to_notion(target_folder_names)

    MemeDBUploader.notion_to_rdb()
