import sergeant


def main():
    parent_package_path = ''
    if '.' in __loader__.name:
        parent_package_path = __loader__.name.rsplit('.', 1)[0]

    supervisor = sergeant.supervisor.Supervisor(
        worker_module_name=f'{parent_package_path}.consumer' if parent_package_path else 'consumer',
        worker_class_name='Worker',
        concurrent_workers=1,
        max_worker_memory_usage=None,
    )
    supervisor.start()


if __name__ == '__main__':
    main()
