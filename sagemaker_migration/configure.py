import configparser
import os

def main():
    ''' '''
    base_path = os.environ['HOME']
    config = configparser.ConfigParser()
    role = input("Enter your AWS role for accessing SageMaker: ")
    config['AWS'] = {}
    config['AWS']['Role'] = role
    with open(f'{base_path}/config.ini', 'w') as fp:
        config.write(fp)

if __name__ == "__main__":
    ''' '''
    main()