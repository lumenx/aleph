import logging

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSON

from aleph.core import db
from aleph.model.metadata import Metadata
from aleph.model.common import TimeStampedModel

log = logging.getLogger(__name__)


class Document(db.Model, TimeStampedModel):
    id = db.Column(db.BigInteger, primary_key=True)
    crawler_tag = db.Column(db.Unicode(65), nullable=False, index=True)
    content_hash = db.Column(db.Unicode(65), nullable=False, index=True)
    _meta = db.Column('meta', JSON)

    @hybrid_property
    def meta(self):
        self._meta = self._meta or {}
        self._meta.crawler_tag = self.crawler_tag
        self._meta.content_hash = self.content_hash
        return Metadata(data=self._meta or {})

    @meta.setter
    def meta(self, meta):
        if isinstance(meta, Metadata):
            # make indexable properties
            self.crawler_tag = meta.crawler_tag
            self.content_hash = meta.content_hash
            meta = meta.data
        self._meta = meta

    @classmethod
    def check_crawler_tag(cls, crawler_tag):
        q = db.session.query(cls).filter_by(crawler_tag=crawler_tag)
        return q.count() > 0

    def __repr__(self):
        return '<Document(%r)>' % (self.id)

    def __unicode__(self):
        return self.id

    def to_dict(self):
        data = self.meta.to_dict()
        data.update({
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        })
        return data