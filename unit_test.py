from pprint import pprint
from torch import optim
import jieba
from ChatBot.network import *
from ChatBot.dataloader import *
from ChatBot.train import *
import json

def test_CBNet():
    network = CBNet(
        embedding_dim=10,
        encoder_hidden_size=64,
        decoder_hidden_size=64,
        attention_score_name="dot",
        vocab_size=15,
        n_layer=1,
        dropout=0
    )

    sentence = torch.tensor([[10, 9, 2, 1, 4, 6], [10, 9, 2, 1, 4, 0], [10, 9, 2, 1, 4, 0]], dtype=torch.int64)
    length = torch.tensor([6, 5, 5])
    result = network(sentence, length, length.max().item(), None, False)
    print(result)


def test_vocab():
    with open("./data/vocab.json", "r", encoding="utf-8") as f:
        a = json.load(fp=f)
    print(a["word2index"]["人工智能"])


def test_dataloader():
    with open("./data/ChatBot/ensemble/small_samples_pairs.json", "r", encoding="utf-8") as f:
        data_dict = json.load(fp=f)
    pairs = data_dict["index_pairs"]
    loader = DataLoader(pairs, batch_size=3)
    for batch in loader:
        x = batch["input_batch_tensor"]
        y = batch["output_batch_tensor"]
        length = batch["input_length_tensor"]
        mask = batch["mask_tensor"]
        print(x)
        print(y)
        print(length)
        print(mask)
        return 

def test_get_datatime_info():
    info = get_datetime_info()
    print(info)

def test_train():
    with open("./data/ChatBot/ensemble/small_samples_pairs.json", "r", encoding="utf-8") as f:
        data_dict = json.load(fp=f)
    with open("./data/ChatBot/ensemble/small_samples_vocab.json", "r", encoding="utf-8") as f:
        vocab_dict = json.load(fp=f)

    model = CBNet(
        embedding_dim=EMBEDDING_DIM,
        encoder_hidden_size=ENCODER_HIDDEN_SIZE,
        decoder_hidden_size=DECODER_HIDDEN_SIZE,
        attention_score_name=ATTENTION_SCORE_NAME,
        vocab_size=vocab_dict["vocab_size"],
    ).to(DEVICE)

    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    train(
        version="0.0.0",
        pairs=data_dict["index_pairs"],
        Epoch=EPOCH_NUM,
        model=model,
        optimizer=optimizer,
        batch_size=BATCH_SIZE,
        save_dir="./dist/ChatBot",
        save_model=True,   
        save_optimizer=False,
        clip_threshold=CLIP_THRESHOLD,
        TF_ratio=TEACHER_FORCING_RATE,
        save_interval=SAVE_INTERVAL,
        display_progress_bar=True
    )

def test_inference():
    start_time = time.time()
    print(color_wrapper("正在加载词表...", GREEN), end="")
    with open("./data/ChatBot/ensemble/small_samples_vocab.json", "r", encoding="utf-8") as f:
        vocab_dict = json.load(fp=f)
    word2index : Dict = vocab_dict["word2index"]
    index2word : Dict = vocab_dict["index2word"]
    print(color_wrapper(" ...完成! 耗时:{:.3f}s".format(time.time() - start_time), GREEN))

    start_time = time.time()
    print(color_wrapper("重构index2word子表...", GREEN), end="")
    index2word = {int(k) : index2word[k] for k in index2word}
    print(color_wrapper(" ...完成! 耗时:{:.3f}s".format(time.time() - start_time), GREEN))

    print("正在加载中文分词模型...")
    print("\033[{}m".format(ORANGE))
    _ = jieba.lcut("你好，世界")
    print("\033[0m")

    start_time = time.time()
    print(color_wrapper("正在创建CBNet推理模型...", GREEN), end="")
    model = CBNet(
        embedding_dim=EMBEDDING_DIM,
        encoder_hidden_size=ENCODER_HIDDEN_SIZE,
        decoder_hidden_size=DECODER_HIDDEN_SIZE,
        attention_score_name=ATTENTION_SCORE_NAME,
        vocab_size=vocab_dict["vocab_size"],
    )
    print(color_wrapper(" ...完成! 耗时{:.3f}s".format(time.time() - start_time), GREEN))

    start_time = time.time()
    print(color_wrapper("正在为CBNet推理模型装载模型参数...", GREEN), end="")
    model_dict : Dict = torch.load("./dist/ChatBot/2021-6-28/23_41_39/model.tar")
    model.load_state_dict(model_dict["model_state_dict"])
    print(color_wrapper(" ...成功载入{}! \033[{}m耗时{:.3f}s".format(color_wrapper("23_41_39/model.tar", PURPLE),GREEN, time.time() - start_time), GREEN))

    print(color_wrapper("请输入你的第一句话", BLUE))
    input_sentence = input("锦恢 > ")
    while input_sentence not in QUIT_WORDS:
        input_index_seq = [word2index.get(word, UNK_TOKEN) for word in jieba.lcut(input_sentence)]
        output_index_seq, _ = model.predict(
            index_seq=torch.LongTensor([input_index_seq]),
            index_seq_length=torch.LongTensor([len(input_index_seq)])
        )
        
        output_sentence = [index2word[index[0]] for index in output_index_seq]
        output_sentence = "".join(output_sentence)
        print(color_wrapper("Minus", PURPLE), ">", color_wrapper(output_sentence, PURPLE))
        input_sentence = input("锦恢 > ")

test_train()