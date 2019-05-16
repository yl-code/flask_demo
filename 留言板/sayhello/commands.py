import click
from sayhello import app, db
from sayhello.models import Message


@app.cli.command()
@click.option("--count", default=10, help="默认造10条假数据哦！")
def forge(count):
    """
    产生 fake 信息
    :param count:
    :return:
    """
    from faker import Faker

    db.drop_all()
    db.create_all()
    fake = Faker("zh_CN")
    click.echo("working..........")

    for i in range(count):
        message = Message(
            name=fake.name(),
            body=fake.sentence(),
           # timestamp=fake.date_time_this_year()
        )
        db.session.add(message)

    db.session.commit()
    click.echo("产生了{}条fake信息".format(count))

@app.cli.command()
@click.option("--drop", is_flag=True, help="创建 after 删除")
def initdb(drop):
    '''
    初始化数据库
    :param drop:
    :return:
    '''
    if drop:
        click.confirm("这个操作将会删除数据库，你确定继续？？？", abort=True)
        db.drop_all()
        click.echo("删除成功，赶紧跑路")
    db.create_all()
    click.echo("创建成功！！！")


