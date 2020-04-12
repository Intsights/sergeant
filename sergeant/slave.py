import sys
import pickle
import traceback


def main():
    data = sys.stdin.buffer.read()
    obj = pickle.loads(data)

    try:
        worker_obj = obj['worker_obj']()
        worker_obj.init_worker()
        worker_obj.work_loop()
        obj['pipe'].send(None)

        return 0
    except KeyboardInterrupt:
        pass
    except Exception as exception:
        obj['pipe'].send(
            {
                'exception': exception,
                'traceback': traceback.format_exc(),
            }
        )

        return -1
    finally:
        try:
            obj['pipe'].close()
        except Exception:
            pass


if __name__ == '__main__':
    main()
