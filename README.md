# jongsul_backend

## API 문서
_API 문서는 [여기](https://snowmate318.github.io/Jongsul_Backend/)에서 확인할 수 있습니다._

## 개요
jongsul_backend은 다음과 같은 기능을 제공하는 프로젝트입니다.
### 프로젝트 구성
#### 데이터베이스 쿼리 요청
![종설-페이지-1 drawio](https://github.com/SnowMate318/Jongsul_Backend/assets/108775585/5ea5eebd-94f5-4083-84ff-34668b9f6bb1)

#### 문제 생성 기능을 사용할 때
![종설-페이지-2 drawio (2)](https://github.com/SnowMate318/Jongsul_Backend/assets/108775585/4e3bd6a1-1dc8-4a5d-a0f2-7bbdf391ef6b)


## 데이터베이스
![Copy of jongsul](https://github.com/SnowMate318/Jongsul_Backend/assets/108775585/3d18f07a-3396-497b-9fd6-8fb089273672)
### 테이블 별
#### User
회원정보를 담고있는 데이블이다
사용자 별 id, 이메일, 비밀번호, 회원 이름, 슈퍼계정, 삭제계정 여부 등 사용자 정보를 담고있다.
#### WebProvider
회원이 소셜로그인을 통해 계정을 생성한 경우, 소셜로그인과 계정 정보를 연결해주기위한 테이블이다.
제공업체 정보, 제공받은 id, 연결된 사용자 id 정보를 담고있다.
#### Library
회원의 라이브러리 정보를 담고있는 테이블이다.
연결된 사용자 아이디, 라이브러리 제목, 최근 접근시간 정보를 담고있다.
#### Directory
회원의 디렉토리 정보를 담고있는 테이블이다.
연결된 라이브러리 아이디, 디렉토리 제목, 최근 접근시간, 문제생성 개념, 스크랩 폴더 여부 정보를 담고있다.
#### Community
회원이 공유한 디렉토리를 다른 사용자가 보고 다운로드 할 수 있도록 하는 게시글의 정보를 담고있는 테이블이다.
공유한 디렉토리 정보, 공유한 사용자 정보, 게시글 제목, 게시글 내용, 업로드 시각, 활성화 여부, 다운로드 횟수 정보를 담고 있다.
#### CommunityTag
커뮤니티 게시글을 쉽게 검색할 수 있도록 태그 정보를 담고있다. 태그 이름 정보를 담고있다.
#### Community_CommunityTag
하나의 커뮤니티에는 0개 이상의 태그가 있을 수 있으며, 하나의 태그에는 1개 이상의 커뮤니티가 연결되어야 한다. 이러한 관계를 표현하기위해 이 테이블을 생성하여 N:M 관계를 표현하였다.
#### Question
생성한 문제에 대한 정보를 담고 있다.
문제 제목, 정답, 해설에 대한 정보를 담고있다.
#### Choice 
생성한 문제의 선택지에 대한 정보를 담고있다. 선택지 번호와, 내용 정보를 담고있다.

## 기능 별
### 인증 및 로그인
![종설-페이지-3 drawio (2)](https://github.com/SnowMate318/Jongsul_Backend/assets/108775585/f47db2e0-7b6a-43ab-9d48-0fdc7484064f)
![종설-페이지-4 drawio](https://github.com/SnowMate318/Jongsul_Backend/assets/108775585/8bec7b0e-abaf-4ff1-b538-925a8ca773a0)
![종설-페이지-5 drawio](https://github.com/SnowMate318/Jongsul_Backend/assets/108775585/aaaa0082-f26e-4314-bbcf-a2bd85bb2517)
![종설-페이지-6 drawio](https://github.com/SnowMate318/Jongsul_Backend/assets/108775585/a2eab2c4-7219-4602-8489-3bb6fce4701a)
Todo: 인증과정 설명

### 요청 별 설명
#### RegisterAPIView
#### AuthAPIView
#### UserAPIView
#### SocialAUthAPIView
#### UserDeleteView

### 문제 폴더 관리 및 문제 풀이
#### LibraryAPIView
#### LibraryDetailAPIView
#### DirectoryAPIView
#### DirectoryDetailAPIView
#### LibraryChangeAPIView
#### DirectoryShareAPIView
#### QuestionAPIView
#### QuestionDetailAPIView
#### QuestionSolveAPIView
#### QuestionScrapAPIView

### 게시글 및 공유문제
#### SharedAPIView
#### SharedUserFilterAPIView
#### SharedDetailAPIView
#### SharedDownloadAPIView



