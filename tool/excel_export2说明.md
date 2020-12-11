导表工具第二版本
===

主要将配表路径可配置化。不用固定放在tool/resource中

# 使用
将**excel_export2_config.py.sample**复制为**excel_export2_config.py**

###配置

里面配置一个key，value。key就是你导表输入的参数，value为excel存放的路径。
excel存放的路径与原本一致

配置举例：

w = "./resource/weapon-card"



###使用方式

python excel_export2.py [配置中的KEY]

