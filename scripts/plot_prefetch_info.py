
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the data from a text file
df = pd.read_csv('./prefetcher_info.txt', sep='\\s+', header=None)
df.columns = ['Address', 'Prefetch Count', 'Estimated Time']

sns.set(font='Times New Roman', font_scale=1.5,
        style='whitegrid', palette='Greys_r')

counts = df['Prefetch Count'].value_counts().sort_index()

plt.figure(figsize=(12, 4))
counts.plot(kind='bar', rot=0)

plt.title('Prefetch Count Distribution')
plt.xlabel('Prefetch Count')
plt.ylabel('Address Count')
plt.tight_layout()
plt.savefig('./prefetch_count.png')
