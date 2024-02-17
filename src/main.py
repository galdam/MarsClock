from marsclock.display import Display


def run():
    disp = Display()
    try:
        disp.loop()
    except Exception as err:
        print(f'Caught error:{err}')
        #disp.shutdown()
        raise err
        
    #finally:
    #    disp.shutdown()
    
if __name__ == '__main__':
    run()
