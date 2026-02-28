import setuptools #导入setuptools打包工具
 
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bit_login", 
    version="3.2.0",
    author="teclab",   
    author_email="admin@teclab.org.cn",
    description="北京理工大学统一身份验证登录模块",
    keywords="BIT, BITCAS, BITLogin, BITWebVPN, BITSSO, BITSSOLogin, BITSSOClient",
    long_description=long_description,   
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        "beautifulsoup4>=4.14.3",
        "cryptography>=46.0.5",
        "fastapi>=0.134.0",
        "pydantic>=2.12.5",
        "requests>=2.32.5",
        "uvicorn>=0.41.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',   
)