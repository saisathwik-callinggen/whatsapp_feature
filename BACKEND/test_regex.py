import re
base_script='If the customer declines: "No problem at all. I'll send over our information so you have it if anything changes. Thank you for your time, and have a great day."'
print(re.sub(r'(?i)Thank you for your time.*?day\.', 'Have a great day.', base_script))
