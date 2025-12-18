# from typing import List


# class TextSplitter:
#     """
#     Docstring for TextSplitter
#     """

#     def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
#         self.chunk_size = chunk_size
#         self.chunk_overlap = chunk_overlap

#     def split_text(self, text: str) -> List[str]:
#         text = text.strip()
#         if not text:
#             return []
        
#         chunks = []
#         start = 0

#         while start < le