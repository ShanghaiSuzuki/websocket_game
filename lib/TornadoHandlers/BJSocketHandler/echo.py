
echo_count = 0


def echo(_cls, _self, message):
    global echo_count
    print("echo(" + str(echo_count) + ") was called : message = " + message)
    payload = {"event" : "echo", "data" : message}
    _cls.send_all(payload)

    """メインエンジンにイベントを登録する例
    def test(*args, **kwargs):
        print("test: message = " + str(args[0]))
        print(args)
        print(kwargs)

    gm = GameMain()
    ct = time.time()
    ct += 10
    gm.add_sched(ct, 1, test, "echo_count = " + str(echo_count),test_value= "nyaa")
    echo_count += 1
    """
