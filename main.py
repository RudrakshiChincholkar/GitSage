from step1_pipeline import run_step1
from file_processor import run_step2_validation

repo_link = "https://github.com/RudrakshiChincholkar/expense-tracker"

downloaded_files = run_step1(repo_link)

print("Downloaded files:", len(downloaded_files))


chunks = run_step2_validation(repo_link)

i = 0
for chunk in chunks:
    if i < 5:
        print(chunk)
        i+=1

# print("Validated files:", len(validated_files))

# for path in list(validated_files.keys())[:10]:
#     print("VALID:", path)
