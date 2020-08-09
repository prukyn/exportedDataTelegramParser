import pandas as pd


class Featurize:
    '''Class create features for imported data '''
    def __init__(self, dataframe: pd.DataFrame, change_names: dict = None):
        '''
        Parameters
        ----------
        :param dataframe: pd.DataFrame
            data in DataFrame format
        :param change_names:
            dict with structure {'old_name': 'new_name', ....}, it uses for update names in dataframe
        '''
        self.df = dataframe
        if change_names:
            self.change_names = change_names

    def _features(self, df):

        def is_text(row: str):
            if row.startswith(('stickers', 'photos', 'voice_messages', 'video_files', 'round_video_messages')):
                return False
            else:
                return True

        df.loc[:, 'timestamp'] = pd.to_datetime(df.loc[:, 'timestamp'], format="%d.%m.%Y %H:%M:%S")
        df.loc[:, 'is_text'] = df.loc[:, 'message'].apply(is_text)
        df.loc[:, 'is_image'] = df.loc[:, 'message'].apply(lambda row: row.startswith('photos'))
        df.loc[:, 'is_video'] = df.loc[:, 'message'].apply(lambda row: row.startswith('video_files'))
        df.loc[:, 'is_video_msg'] = df.loc[:, 'message'].apply(lambda row: row.startswith('round_video_messages'))
        df.loc[:, 'is_sticker'] = df.loc[:, 'message'].apply(lambda row: row.startswith('stickers'))
        df.loc[:, 'is_bot'] = df.loc[:, 'author'].str.contains('Bot|bot|BOT|KPI', regex=True)
        df.loc[:, 'is_forwarded'] = df.loc[:, 'author'].str.contains('\d+\.\d+\.\d+\W\d+\:\d+:\d+', regex=True)
        df.loc[:, 'is_voice'] = df.loc[:, 'message'].apply(lambda row: row.startswith('voice_messages'))
        df.loc[:, 'is_link'] = df.loc[:, 'message'].str.contains('https?\:\/\/', regex=True)
        return df

    def process(self):
        df = self.df.dropna()
        df = df.drop(df.index[df.author.str.contains('via @')])
        if self.change_names:
            df.loc[:, 'author'] = df.loc[:, 'author'].apply(
                lambda name: self.change_names[name] if name in self.change_names.keys() else name
            )
        df = self._features(df)
        return df

