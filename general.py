import yaml


def load_config(file_path='config.yaml'):
    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f'未配置{file_path}')
        return None
        # raise FileNotFoundError(f"配置文件 {file_path} 不存在！")
    except Exception as e:
        raise Exception(f"配置解析失败: {str(e)}")


def get_config(config, default_config, key_list):
    use_config = True
    if config is not None:
        sub_config = config
        for key in key_list:
            if key in sub_config:
                sub_config = sub_config[key]
            else:
                use_config = False
                break
    else:
        use_config = False
    if use_config:
        return sub_config
    else:
        sub_config = default_config
        for key in key_list:
            sub_config = sub_config[key]
        return sub_config
