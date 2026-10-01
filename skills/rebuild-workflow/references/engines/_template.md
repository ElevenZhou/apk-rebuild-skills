# 引擎：<名称>（⚠️ 待真实案例验证）

> 遇到新引擎时复制本模板为 `<引擎>.md`，项目过程中边做边填，收尾时 PR。未经真实项目验证的内容必须标 `未验证`。

## 识别特征（S1）
- 特征 so / 目录 / 文件头：
- 是否常见加固/加密：

## 解包与回导工具（S3）
| 资源类型 | 工具 | 命令 | 验证状态 |
|---|---|---|---|

## 已知候选工具（未验证，供起步参考）
- Unity Mono：AssetRipper / AssetStudio，dnSpy/ILSpy 看 Assembly-CSharp.dll
- Unity IL2CPP：Il2CppDumper + AssetRipper（脚本只能还原签名，逻辑需重写）
- Cocos Creator / cocos2d-x：解 jsc（xxtea 密钥在 so 里）/ 资源 plist、atlas
- 原生 Android：apktool + jadx

## 开发（S5）
- 冒烟命令：
- 测试运行方式：

## 打包（S7）
- 工具链版本：
- 签名方式：
- 已踩坑：

## 案例
- 项目 <代号>（日期）：一句话结论
